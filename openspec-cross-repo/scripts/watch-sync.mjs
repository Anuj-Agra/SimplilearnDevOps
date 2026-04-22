#!/usr/bin/env node
/**
 * OpenSpec Cross-Repo Watcher
 * Monitors both repos' openspec/changes/ directories.
 * Alerts when cross-repo action is needed.
 * 
 * Usage: node scripts/watch-sync.mjs --java ../my-java-service --angular ../my-angular-app
 */
import { readdir, readFile, stat } from "node:fs/promises";
import { join, resolve } from "node:path";
import { existsSync } from "node:fs";
import { argv } from "node:process";

const args = parseArgs(argv.slice(2));
const JAVA_REPO = resolve(args.java || "../my-java-service");
const ANGULAR_REPO = resolve(args.angular || "../my-angular-app");
const POLL_INTERVAL = parseInt(args.interval || "3000", 10);
const JAVA_CHANGES = join(JAVA_REPO, "openspec/changes");
const ANGULAR_CHANGES = join(ANGULAR_REPO, "openspec/changes");
const JAVA_SPECS = join(JAVA_REPO, "openspec/specs");
const ANGULAR_SPECS = join(ANGULAR_REPO, "openspec/specs");

const API_KEYWORDS = ["endpoint","api","controller","service","dto","model","request","response","http","rest","path","route","schema","interface","observable","httpclient","@GetMapping","@PostMapping","@PutMapping","@DeleteMapping","ADDED Requirements","MODIFIED Requirements","REMOVED Requirements"];

let prevState = { java: {}, angular: {} };

async function main() {
  printBanner(); validatePaths();
  prevState.java = await snapshot(JAVA_CHANGES);
  prevState.angular = await snapshot(ANGULAR_CHANGES);
  const jOk = existsSync(JAVA_SPECS) && (await listDirs(JAVA_SPECS)).length > 0;
  const aOk = existsSync(ANGULAR_SPECS) && (await listDirs(ANGULAR_SPECS)).length > 0;
  if (!jOk || !aOk) printAlert("SPECS MISSING", `${!jOk?"☕ Java":""}${!jOk&&!aOk?" + ":""}${!aOk?"🅰️ Angular":""} repo has no specs.`, "Run /xspec-auto in Copilot Chat to bootstrap.");
  printStatus(prevState); log("👀 Watching for changes...\n");
  while (true) { await sleep(POLL_INTERVAL); await check(); }
}

async function check() {
  const cj = await snapshot(JAVA_CHANGES), ca = await snapshot(ANGULAR_CHANGES);
  for (const [id, info] of Object.entries(cj)) {
    if (!prevState.java[id]) await onNew("java", id, info, ca);
    else if (info.mtime > prevState.java[id].mtime) await onMod("java", id, info, ca);
  }
  for (const [id, info] of Object.entries(ca)) {
    if (!prevState.angular[id]) await onNew("angular", id, info, cj);
    else if (info.mtime > prevState.angular[id].mtime) await onMod("angular", id, info, cj);
  }
  for (const id of Object.keys(prevState.java)) if (!cj[id]) { log(`📦 Java archived: ${id}`); if (ca[id]) printAlert("ARCHIVE SYNC", `Java archived "${id}" but Angular still has it active.`, "Archive in Angular too, then /xspec-sync-contract"); }
  for (const id of Object.keys(prevState.angular)) if (!ca[id]) { log(`📦 Angular archived: ${id}`); if (cj[id]) printAlert("ARCHIVE SYNC", `Angular archived "${id}" but Java still has it active.`, "Archive in Java too, then /xspec-sync-contract"); }
  prevState = { java: cj, angular: ca };
}

async function onNew(repo, id, info, other) {
  const rl = repo==="java"?"☕ Java":"🅰️ Angular", ol = repo==="java"?"🅰️ Angular":"☕ Java";
  log(`\n🆕 New change in ${rl}: ${id}`);
  if (!await isApi(repo==="java"?JAVA_CHANGES:ANGULAR_CHANGES, id)) { log("   ↳ Internal — no cross-repo action"); return; }
  if (other[id]) { log(`   ↳ ✅ Already linked in ${ol}`); return; }
  printAlert("PROPAGATION NEEDED", `${rl} created API-surface change "${id}" with no link in ${ol}.`, `Run /xspec-auto — or /xspec-propagate ${id}`);
}

async function onMod(repo, id, info, other) {
  const rl = repo==="java"?"☕ Java":"🅰️ Angular";
  const tp = join(repo==="java"?JAVA_CHANGES:ANGULAR_CHANGES, id, "tasks.md");
  if (!existsSync(tp)) return;
  try {
    const c = await readFile(tp,"utf-8"), tot=(c.match(/- \[[ x]\]/g)||[]).length, done=(c.match(/- \[x\]/g)||[]).length;
    if (tot>0 && done===tot) {
      log(`\n✅ ${rl} "${id}": All ${tot} tasks complete!`);
      if (other[id]) {
        const otp = join(repo==="java"?ANGULAR_CHANGES:JAVA_CHANGES, id, "tasks.md");
        if (existsSync(otp)) { const oc=await readFile(otp,"utf-8"), ot=(oc.match(/- \[[ x]\]/g)||[]).length, od=(oc.match(/- \[x\]/g)||[]).length;
          if (ot>0&&od===ot) printAlert("BOTH SIDES COMPLETE", `"${id}" is fully implemented in both repos!`, "Run /xspec-auto to verify types, then /opsx:archive in each repo.");
          else log(`   ↳ ${repo==="java"?"🅰️ Angular":"☕ Java"} still has ${ot-od}/${ot} tasks remaining`);
        }
      }
    }
  } catch {}
}

async function isApi(dir, id) {
  if (existsSync(join(dir,id,"specs"))) return true;
  for (const f of ["proposal.md","design.md"]) {
    const p=join(dir,id,f); if (!existsSync(p)) continue;
    try { const c=(await readFile(p,"utf-8")).toLowerCase(); if (API_KEYWORDS.some(k=>c.includes(k.toLowerCase()))) return true; } catch {}
  }
  return false;
}

async function snapshot(dir) {
  const s = {}; if (!existsSync(dir)) return s;
  for (const e of await listDirs(dir)) {
    if (e==="archive") continue; const cp=join(dir,e);
    try { const st=await stat(cp); if (!st.isDirectory()) continue; const mt=await latestMt(cp);
      let tp=null; const tf=join(cp,"tasks.md"); if (existsSync(tf)) try { const c=await readFile(tf,"utf-8"); tp={done:(c.match(/- \[x\]/g)||[]).length, total:(c.match(/- \[[ x]\]/g)||[]).length}; } catch {}
      s[e]={mtime:mt, hasProposal:existsSync(join(cp,"proposal.md")), hasTasks:existsSync(join(cp,"tasks.md")), hasSpecs:existsSync(join(cp,"specs")), taskProgress:tp};
    } catch {}
  }
  return s;
}

async function latestMt(d) { let l=0; try { for (const e of await readdir(d,{withFileTypes:true})) { const p=join(d,e.name),s=await stat(p); if (s.isDirectory()) { const m=await latestMt(p); if(m>l)l=m; } else { if(s.mtimeMs>l)l=s.mtimeMs; } } } catch {} return l; }
async function listDirs(d) { try { return (await readdir(d,{withFileTypes:true})).filter(e=>e.isDirectory()).map(e=>e.name); } catch { return []; } }
function sleep(ms) { return new Promise(r=>setTimeout(r,ms)); }
function parseArgs(a) { const r={}; for(let i=0;i<a.length;i++) if(a[i].startsWith("--")&&i+1<a.length){r[a[i].slice(2)]=a[i+1];i++;} return r; }
function validatePaths() { if(!existsSync(JAVA_REPO)){error(`Java repo not found: ${JAVA_REPO}\nPass --java /path`);process.exit(1);} if(!existsSync(ANGULAR_REPO)){error(`Angular repo not found: ${ANGULAR_REPO}\nPass --angular /path`);process.exit(1);} log(`☕ Java:    ${JAVA_REPO}`); log(`🅰️  Angular: ${ANGULAR_REPO}`); }

function printBanner() { console.log(`\n╔══════════════════════════════════════════════════════════╗\n║          OpenSpec Cross-Repo Watcher                     ║\n║          Monitoring for cross-repo changes...            ║\n╚══════════════════════════════════════════════════════════╝\n`); }
function printStatus(st) { const jc=Object.entries(st.java),ac=Object.entries(st.angular); log(`\n📊 Current State:`); log(`   ☕ Java: ${jc.length} active`); for(const[id,i]of jc){const t=i.taskProgress?` [${i.taskProgress.done}/${i.taskProgress.total}]`:"",lk=ac.some(([a])=>a===id)?" 🔗":"";log(`      └── ${id}${t}${lk}`);} log(`   🅰️  Angular: ${ac.length} active`); for(const[id,i]of ac){const t=i.taskProgress?` [${i.taskProgress.done}/${i.taskProgress.total}]`:"",lk=jc.some(([j])=>j===id)?" 🔗":"";log(`      └── ${id}${t}${lk}`);} }
function printAlert(type,msg,action) { const w=57; console.log(`\n┌${"─".repeat(w)}┐\n│ ⚡ ${type.padEnd(w-4)}│\n├${"─".repeat(w)}┤\n│ ${wrap(msg,w-2).join("\n│ ")} │\n├${"─".repeat(w)}┤\n│ 👉 ${wrap(action,w-5).join("\n│    ")} │\n└${"─".repeat(w)}┘\n`); }
function wrap(t,w) { const words=t.split(" "),lines=[]; let c=""; for(const word of words){if((c+" "+word).trim().length>w){lines.push(c.padEnd(w));c=word;}else{c=(c+" "+word).trim();}} if(c)lines.push(c.padEnd(w)); return lines; }
function log(m) { console.log(`[${new Date().toLocaleTimeString("en-GB",{hour12:false})}] ${m}`); }
function error(m) { console.error(`❌ ${m}`); }

main().catch(e=>{error(`Crashed: ${e.message}`);process.exit(1);});
