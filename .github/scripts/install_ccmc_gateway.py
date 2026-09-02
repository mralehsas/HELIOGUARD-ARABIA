#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

INDEX = Path("index.html")
RECENT = Path("data/ccmc-scoreboard-recent.json")
HIST = Path("data/ccmc-scoreboard-90d.json")
CACHE_WORKFLOW = Path(".github/workflows/ccmc-cache.yml")

MARKERS = [
    "fetchScoreboardResilient",
    "scoreboardGatewayRecent",
    "scoreboardGateway90",
    "HELIOGUARD CCMC Gateway",
    "Connected — GitHub Gateway",
]


def gateway_payload_valid(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    return (
        data.get("schema") == "HELIOGUARD_CCMC_GATEWAY_V1"
        and isinstance(data.get("events"), list)
        and bool(data.get("fetchedAt"))
        and str(data.get("source", "")).startswith("https://kauai.ccmc.gsfc.nasa.gov/")
    )


def contract_status() -> tuple[bool, list[str]]:
    s = INDEX.read_text(encoding="utf-8")
    missing = [m for m in MARKERS if m not in s]
    if not gateway_payload_valid(RECENT):
        missing.append(str(RECENT))
    if not gateway_payload_valid(HIST):
        missing.append(str(HIST))
    if not CACHE_WORKFLOW.exists():
        missing.append(str(CACHE_WORKFLOW))
    if "fetchJson(scoreboardUrl({CMEID:id,skipNoArrivalObservedCMEs:false,closeOutCMEsOnly:false}),25000)" in s:
        missing.append("forecast direct-only call remains")
    if "fetchJson(scoreboardUrl({CMEtimeStart:start,CMEtimeEnd:end,skipNoArrivalObservedCMEs:true,closeOutCMEsOnly:true}),30000)" in s:
        missing.append("validation direct-only call remains")
    return not missing, missing


def test_contract() -> None:
    ok, missing = contract_status()
    if not ok:
        print("CCMC gateway contract NOT satisfied:")
        for item in missing:
            print(" -", item)
        raise SystemExit(1)
    print("CCMC gateway contract: GREEN")


def replace_once(s: str, old: str, new: str, label: str) -> str:
    count = s.count(old)
    if count != 1:
        raise RuntimeError(f"Unsafe {label} patch count: {count}")
    return s.replace(old, new, 1)


def apply_patch() -> None:
    s = INDEX.read_text(encoding="utf-8")
    if all(m in s for m in MARKERS):
        print("Frontend gateway markers already installed; no patch required.")
        return

    s = replace_once(
        s,
        '    scoreboard: "https://kauai.ccmc.gsfc.nasa.gov/CMEscoreboard/WS/get/predictions",',
        '    scoreboard: "https://kauai.ccmc.gsfc.nasa.gov/CMEscoreboard/WS/get/predictions",\n'
        '    scoreboardGatewayRecent: "data/ccmc-scoreboard-recent.json",\n'
        '    scoreboardGateway90: "data/ccmc-scoreboard-90d.json",',
        "CONFIG",
    )

    old_ccmc = '    {id:"ccmc",agency:"NASA CCMC",name:"CME Scoreboard",role:"توقعات وصول CME متعددة النماذج والتحقق التاريخي.",fresh:null,endpoints:[{label:"Predictions",url:scoreboardUrl({CMEtimeStart:r30.start,CMEtimeEnd:r30.end,skipNoArrivalObservedCMEs:false,closeOutCMEsOnly:false}),kind:"json",timeout:30000}],time:d=>null,count:d=>Array.isArray(d)?d.length:(Array.isArray(d?.events)?d.events.length:0),valid:d=>Array.isArray(d)||Array.isArray(d?.events)||typeof d==="object"},'
    new_ccmc = '    {id:"ccmc",agency:"NASA CCMC",name:"CME Scoreboard",role:"توقعات وصول CME متعددة النماذج والتحقق التاريخي.",fresh:180,endpoints:[{label:"HELIOGUARD CCMC Gateway",url:`${CONFIG.endpoints.scoreboardGatewayRecent}?v=${Date.now()}`,kind:"json",timeout:12000},{label:"NASA CCMC Direct",url:scoreboardUrl({CMEtimeStart:r30.start,CMEtimeEnd:r30.end,skipNoArrivalObservedCMEs:false,closeOutCMEsOnly:false}),kind:"json",timeout:30000}],time:d=>d?.fetchedAt||null,count:d=>Array.isArray(d)?d.length:(Array.isArray(d?.events)?d.events.length:0),valid:d=>Array.isArray(d)||Array.isArray(d?.events)||typeof d==="object"},'
    s = replace_once(s, old_ccmc, new_ccmc, "CCMC service")

    anchor = 'function scoreboardUrl(params){const u=new URL(CONFIG.endpoints.scoreboard);Object.entries(params).forEach(([k,v])=>v!==null&&v!==undefined&&v!==""&&u.searchParams.set(k,String(v)));return u.toString()}'
    helper = r'''
function filterGatewayScoreboard(events,params={}){
  let out=Array.isArray(events)?events.slice():[];
  if(params.CMEID)out=out.filter(e=>String(e?.cmeID||"")===String(params.CMEID));
  if(params.CMEtimeStart&&params.CMEtimeEnd){const a=Date.parse(params.CMEtimeStart+"T00:00:00Z"),b=Date.parse(params.CMEtimeEnd+"T23:59:59Z");out=out.filter(e=>{const t=Date.parse(e?.observedTime||"");return Number.isFinite(t)&&t>=a&&t<=b})}
  if(params.skipNoArrivalObservedCMEs===true||String(params.skipNoArrivalObservedCMEs)==="true")out=out.filter(e=>e?.noArrivalObserved!==true);
  if(params.closeOutCMEsOnly===true||String(params.closeOutCMEsOnly)==="true")out=out.filter(e=>Boolean(e?.arrivalTime)||e?.noArrivalObserved===true);
  return out
}
async function fetchScoreboardGatewayFile(url,params,timeout){const raw=await fetchJson(`${url}?v=${Date.now()}`,timeout);const events=normalizeScoreboardPayload(raw);return {raw,events:filterGatewayScoreboard(events,params)}}
async function fetchScoreboardResilient(params={},timeout=25000){
  let directError=null;
  try{const raw=await fetchJson(scoreboardUrl(params),timeout);state.forecast.scoreboardProvider="direct";return raw}catch(err){directError=err;console.warn("CCMC direct blocked/unavailable; trying HELIOGUARD gateway:",err)}
  const validation=Boolean(params?.CMEtimeStart&&params?.CMEtimeEnd&&(params?.closeOutCMEsOnly===true||String(params?.closeOutCMEsOnly)==="true"));
  const first=validation?CONFIG.endpoints.scoreboardGateway90:CONFIG.endpoints.scoreboardGatewayRecent;
  const second=validation?CONFIG.endpoints.scoreboardGatewayRecent:CONFIG.endpoints.scoreboardGateway90;
  try{
    let r=await fetchScoreboardGatewayFile(first,params,12000);
    if(params.CMEID&&!r.events.length)r=await fetchScoreboardGatewayFile(second,params,12000);
    if(params.CMEID&&!r.events.length)throw directError||new Error("CME not present in gateway cache");
    state.forecast.scoreboardProvider="gateway";
    return r.events
  }catch(gatewayError){console.warn("HELIOGUARD CCMC gateway unavailable:",gatewayError);throw directError||gatewayError}
}
function markScoreboardProviderStatus(){const el=$("statusScoreboard");if(!el||!state.liveStarted)return;if(state.forecast.scoreboardProvider==="gateway"){el.textContent=hgT("متصل — بوابة GitHub","Connected — GitHub Gateway");el.style.color="var(--green)"}else if(state.forecast.scoreboardProvider==="direct"){el.textContent=hgT("متصل مباشر","Directly Connected");el.style.color="var(--green)"}}
'''
    s = replace_once(s, anchor, anchor + helper, "helper")

    s = replace_once(
        s,
        'fetchJson(scoreboardUrl({CMEID:id,skipNoArrivalObservedCMEs:false,closeOutCMEsOnly:false}),25000)',
        'fetchScoreboardResilient({CMEID:id,skipNoArrivalObservedCMEs:false,closeOutCMEsOnly:false},25000)',
        "forecast call",
    )
    s = replace_once(
        s,
        'fetchJson(scoreboardUrl({CMEtimeStart:start,CMEtimeEnd:end,skipNoArrivalObservedCMEs:true,closeOutCMEsOnly:true}),30000)',
        'fetchScoreboardResilient({CMEtimeStart:start,CMEtimeEnd:end,skipNoArrivalObservedCMEs:true,closeOutCMEsOnly:true},30000)',
        "validation call",
    )

    s = replace_once(
        s,
        'setServerStatus("scoreboard",true);$("forecastDot")',
        'setServerStatus("scoreboard",true);markScoreboardProviderStatus();$("forecastDot")',
        "forecast status",
    )
    s = replace_once(
        s,
        'setServerStatus("scoreboard",true)}catch(err){console.error("Validation:',
        'setServerStatus("scoreboard",true);markScoreboardProviderStatus()}catch(err){console.error("Validation:',
        "validation status",
    )

    INDEX.write_text(s, encoding="utf-8")
    print("Frontend gateway patch applied.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["test", "apply"])
    args = parser.parse_args()
    if args.mode == "test":
        test_contract()
    else:
        apply_patch()


if __name__ == "__main__":
    main()
