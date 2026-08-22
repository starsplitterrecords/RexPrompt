#!/usr/bin/env python3
import base64, gzip, json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "data/shows/vikings-2026-s1"
SRC = ROOT.parent / "recovered/Visions/vikings_2026__v2 (12).json"

def line(speaker, handle, text):
    return {"speaker": speaker, "characterHandle": handle, "text": text}

P = [
 ("The Forty-Eight-Hour Walk", "Busy NYC sidewalk", "Carrie gets Bjorn to the bank before provisional status expires.", 4, [line("Carrie","@vik.Carrie","Forty-eight hours. No account, no apartment."),line("Bjorn","@vik.Bjorn","Then we claim the hoard before sunset."),line("Gunnar","@vik.Gunnar","I have marked the iron worm's exits."),line("Carrie","@vik.Carrie","Of course you have.")]),
 ("A Retail Fortress", "Outside a Chase branch", "Bjorn discovers that the hoard is protected by glass and customer service.", 4, [line("Bjorn","@vik.Bjorn","This is the fortress?"),line("Carrie","@vik.Carrie","This is the branch."),line("Gunnar","@vik.Gunnar","A thrown turnip would breach it."),line("Carrie","@vik.Carrie","Please don't test that.")]),
 ("Gary of the Bad Knee", "Chase vestibule", "The security guard becomes a person rather than a warrior in Bjorn's imagined system.", 4, [line("Bjorn","@vik.Bjorn","Gary guards the inner vault?"),line("Carrie","@vik.Carrie","Gary helps people use the ATM."),line("Gary","@vik.Gary","Morning."),line("Bjorn","@vik.Bjorn","Your knee has seen battle.")]),
 ("Fields of Fire", "Chase lobby", "Gunnar maps cameras, exits, and the teller line on Carrie's grocery bag.", 4, [line("Carrie","@vik.Carrie","That had my bagel in it."),line("Gunnar","@vik.Gunnar","The grease makes excellent tracing parchment."),line("Carrie","@vik.Carrie","Stop mapping the bank."),line("Gunnar","@vik.Gunnar","Then it should stop having weaknesses.")]),
 ("The Footprint", "Teller line", "Carrie converts DTI identity into ordinary bank boxes while Bjorn watches the ritual.", 4, [line("Carrie","@vik.Carrie","The red stamp makes this primary identification."),line("Kevin","@vik.Kevin","He was born in eight seventy-nine?"),line("Carrie","@vik.Carrie","Not nineteen eighty-seven. Eight seventy-nine."),line("Bjorn","@vik.Bjorn","The scribe reads slowly.")]),
 ("Address Unknown", "Teller counter", "The bank's ordinary address requirement nearly defeats the application.", 4, [line("Kevin","@vik.Kevin","I still need proof of address."),line("Carrie","@vik.Carrie","DTI placed him there. DTI pays the lease."),line("Kevin","@vik.Kevin","The system needs a document."),line("Carrie","@vik.Carrie","I am holding the document.")]),
 ("Worthier Currency", "Teller counter", "Bjorn produces hacksilver as a sincere opening deposit.", 3, [line("Bjorn","@vik.Bjorn","Then record this: Bjorn brings worthy silver."),line("Kevin","@vik.Kevin","Is that scrap metal?"),line("Carrie","@vik.Carrie","Don't call it that.")]),
 ("The Sun Disk", "Teller counter", "An MTA token briefly appears to bridge Bjorn's world and modern value.", 4, [line("Bjorn","@vik.Bjorn","This disk opens the gates beneath the earth."),line("Kevin","@vik.Kevin","That's a subway token."),line("Gunnar","@vik.Gunnar","A key to the iron worm."),line("Kevin","@vik.Kevin","They stopped taking those in 2003.")]),
 ("Eleven Percent", "Teller counter", "Kevin suggests Coinstar and accidentally turns a banking problem into an insult.", 4, [line("Kevin","@vik.Kevin","Coinstar might take the coins. It keeps eleven percent."),line("Bjorn","@vik.Bjorn","Eleven?"),line("Carrie","@vik.Carrie","Nobody is mounting the Coinstar on anything."),line("Bjorn","@vik.Bjorn","It demands a raider's share without raiding.")]),
 ("Carrie's Fifty", "Teller counter", "Carrie quietly supplies the opening deposit rather than letting the mandate fail.", 4, [line("Carrie","@vik.Carrie","Fifty dollars. Legal tender. Open the account."),line("Kevin","@vik.Kevin","Is that your money?"),line("Carrie","@vik.Carrie","It is his money now."),line("Bjorn","@vik.Bjorn","You place silver in my hoard?")]),
 ("A Debt Named Otherwise", "Teller counter", "Bjorn refuses charity; Carrie reframes the money as a recoverable DTI advance.", 4, [line("Bjorn","@vik.Bjorn","I do not take alms."),line("Carrie","@vik.Carrie","Good. It's an advance."),line("Bjorn","@vik.Bjorn","At what tribute?"),line("Carrie","@vik.Carrie","Fifty dollars. No heads. No livestock.")]),
 ("The Card", "Teller desk", "The debit card makes abstract money feel like confiscation.", 4, [line("Kevin","@vik.Kevin","This card accesses the account."),line("Bjorn","@vik.Bjorn","Where is the silver?"),line("Kevin","@vik.Kevin","In the account."),line("Bjorn","@vik.Bjorn","You have hidden it inside the blue tile?")]),
 ("Proof Without Treasure", "Teller desk", "Carrie demonstrates a balance on the banking app, which Bjorn rejects as a picture of wealth.", 4, [line("Carrie","@vik.Carrie","See? Fifty dollars."),line("Bjorn","@vik.Bjorn","I see light shaped like numbers."),line("Carrie","@vik.Carrie","That is what money looks like now."),line("Bjorn","@vik.Bjorn","Then money has become cowardly.")]),
 ("Silas Goes Live", "Sidewalk outside the bank", "Silas narrates Gunnar's map as evidence of a planned raid and posts it live.", 4, [line("Silas","@vik.Silas","DTI subjects are casing a financial institution in broad daylight."),line("Silas","@vik.Silas","There. The hand-drawn floor plan."),line("Gunnar","@vik.Gunnar","The watcher across the street has shown himself."),line("Carrie","@vik.Carrie","Do not go outside.")]),
 ("The Wrong Alarm", "Chase lobby", "Gunnar approaches the glass to photograph Silas; Silas backs into the panic button housing outside.", 4, [line("Gunnar","@vik.Gunnar","A scout should be answered."),line("Carrie","@vik.Carrie","With a complaint, not an axe."),line("Silas","@vik.Silas","He's advancing."),line("Gary","@vik.Gary","Everybody stay calm.")]),
 ("Managerial Intervention", "Chase manager desk", "The silent alarm brings Henderson, who sees a compliance and publicity problem rather than a raid.", 4, [line("Henderson","@vik.Henderson","Why is our branch trending?"),line("Kevin","@vik.Kevin","They brought silver."),line("Carrie","@vik.Carrie","They brought identification."),line("Bjorn","@vik.Bjorn","And your toll-keeper refused tribute.")]),
 ("Terms of the Hoard", "Chase manager desk", "Henderson offers a safe-deposit appraisal referral while keeping the checking account separate.", 4, [line("Henderson","@vik.Henderson","We can document the metal and refer it for appraisal. We cannot deposit it as currency."),line("Bjorn","@vik.Bjorn","You will witness the hoard, but not swallow it."),line("Carrie","@vik.Carrie","That's unusually close to correct."),line("Henderson","@vik.Henderson","And the fifty remains available today.")]),
 ("The Map Becomes Useful", "Chase manager desk", "Gunnar's transit map proves the branch address and route needed for in-person access.", 4, [line("Henderson","@vik.Henderson","He needs a reliable way to reach a branch."),line("Gunnar","@vik.Gunnar","The iron worm reaches three of your glass tents."),line("Carrie","@vik.Carrie","You mapped all three?"),line("Gunnar","@vik.Gunnar","Four. One closes before sunset.")]),
 ("Silas's Own Evidence", "Chase lobby and sidewalk", "Carrie uses Silas's livestream to show that the group arrived under DTI supervision, defeating his claim.", 4, [line("Carrie","@vik.Carrie","Your video shows them entering with their caseworker and waiting in line."),line("Silas","@vik.Silas","It shows reconnaissance."),line("Henderson","@vik.Henderson","It shows a customer appointment."),line("Gary","@vik.Gary","And you leaning on our alarm box.")]),
 ("A Thing That Exists", "Chase manager desk", "Bjorn accepts the account only if the institution provides tangible acknowledgment.", 4, [line("Bjorn","@vik.Bjorn","A pact with no object is wind."),line("Carrie","@vik.Carrie","He needs something physical."),line("Henderson","@vik.Henderson","We discontinued passbooks."),line("Kevin","@vik.Kevin","We still have the new-account promotion.")]),
 ("Tribute", "Chase supply room / manager desk", "Henderson produces the promotional metal toaster; the absurd object satisfies Bjorn's demand for witnessed exchange.", 4, [line("Henderson","@vik.Henderson","Complimentary with qualifying direct deposit."),line("Carrie","@vik.Carrie","He doesn't have direct deposit."),line("Henderson","@vik.Henderson","Today he does."),line("Bjorn","@vik.Bjorn","The hoard yields iron and controlled fire.")]),
 ("The Mark", "Chase manager desk", "Bjorn signs, pockets the debit card, and formally names Carrie as creditor rather than benefactor.", 4, [line("Bjorn","@vik.Bjorn","Carrie of the Clipboard. Your fifty will be returned first."),line("Carrie","@vik.Carrie","After rent."),line("Bjorn","@vik.Bjorn","After rent."),line("Kevin","@vik.Kevin","Please sign on the line.")]),
 ("The Iron Worm, Reconsidered", "L train platform", "Gunnar uses the account route map and MetroCard logic to bring the group home.", 4, [line("Gunnar","@vik.Gunnar","The worm is unreliable, but its tunnels are honest."),line("Carrie","@vik.Carrie","That may be the nicest thing anyone has said about the L train."),line("Bjorn","@vik.Bjorn","Guard the fire-box."),line("Gunnar","@vik.Gunnar","With my life.")]),
 ("First Purchase", "Bushwick apartment kitchen", "The toaster becomes useful, the account becomes real, and Carrie is quietly included in the household.", 4, [line("Bjorn","@vik.Bjorn","The blue tile bought bread without surrendering silver."),line("Carrie","@vik.Carrie","That's the basic idea."),line("Gunnar","@vik.Gunnar","The fire-box has two gates."),line("Bjorn","@vik.Bjorn","Sit. The first toast is owed to our creditor.")]),
]

def panel_plan(page, count):
    beats=[]
    for i in range(count):
        beats.append({"panel":i+1,"shotType":["wide","medium","close-up","insert"][i%4],"action":page[2],"dialogueIndices":[i] if i < len(page[4]) else [],"captionIndices":[],"readerFunction":"Advance the page beat clearly; preserve speaker identity and left-to-right balloon order."})
    return beats

def make_page(i, spec):
    title, setting, summary, panels, dialogue = spec
    return {"id":f"VIK_S1E02_P{i:02d}","episode":"S1E02","issue":2,"page":i,"title":title,"setting":setting,"summary":summary,"panelCount":panels,"layoutName":["FEATURE_DETAIL","FOUR_PANEL","DIALOGUE_ROW","CINEMATIC_STRIP"][i%4],"focalPanelIndex":panels-1,"panelPlan":panel_plan(spec,panels),"dialogueInline":[dict(fid=f"VIK_S1E02_P{i:02d}_L{j+1:02d}",**d) for j,d in enumerate(dialogue)],"directionInline":[{"type":"story","text":summary},{"type":"tone","text":"Bright ordinary-2026 documentary sitcom realism; municipal competence and deadpan behavior, never mythic spectacle."},{"type":"continuity","text":"Use released Vikings 2026 Issue 1 as visual canon for Bjorn, Gunnar, Carrie, Silas, costumes, proportions, and acting."},{"type":"location","text":f"Maintain one stable physical layout for {setting}; preserve entrances, counters, glass walls, furniture, and character sides across continuous pages."},{"type":"lettering","text":"Use exact dialogueInline text with clear speaker attribution, natural balloon order, and no invented or duplicated words."}],"status":"production-ready","source":"enhanced from full Vikings export; released Issue 1 fixed canon"}

def main():
    (SHOW/"encoded").mkdir(parents=True, exist_ok=True)
    (SHOW/"source").mkdir(parents=True, exist_ok=True)
    source_bytes=SRC.read_bytes()
    encoded_source=base64.b64encode(gzip.compress(source_bytes,compresslevel=9,mtime=0)).decode()
    chunk_size=100_000
    chunks=[]
    for index,start in enumerate(range(0,len(encoded_source),chunk_size),1):
        name=f"vikings_2026_full_export.part{index:02d}.json.gzb64"
        (SHOW/"source"/name).write_text(encoded_source[start:start+chunk_size]+"\n")
        chunks.append(name)
    (SHOW/"source/manifest.json").write_text(json.dumps({"sourceFile":"vikings_2026__v2 (12).json","encoding":"gzip-base64","orderedParts":chunks,"decodedBytes":len(source_bytes)},indent=2)+"\n")
    source=json.loads(source_bytes)
    chars={c["id"]:{"name":c.get("name"),"handle":c.get("handle"),"sourceId":c["id"],"canonRule":"Released StarSplitterVisions art controls appearance. Stale neo-noir/cyberpunk descriptions in the source export are non-canon."} for c in source["characters"]}
    chars.update({"gary":{"name":"Gary","handle":"@vik.Gary","role":"Chase security guard; ordinary, calm, bad knee"},"kevin":{"name":"Kevin","handle":"@vik.Kevin","role":"Young Chase teller; procedural, nervous, not foolish"},"henderson":{"name":"Henderson","handle":"@vik.Henderson","role":"Branch manager; pragmatic institutional problem-solver"}})
    (SHOW/"characters.json").write_text(json.dumps(chars,indent=2)+"\n")
    settings={str(i):x for i,x in enumerate(["Busy NYC sidewalk","Chase exterior and vestibule","Chase lobby and teller line","Chase manager desk","L train platform and car","Bushwick apartment kitchen"])}
    (SHOW/"settings.json").write_text(json.dumps(settings,indent=2)+"\n")
    plan={"series":"Vikings 2026","season":"S1","canonBoundary":"Issue 1 released in StarSplitterVisions is fixed canon.","issues":[{"issue":1,"title":"Landfall Bushwick","status":"released canon"},{"issue":2,"title":"The Hoard of Chase Bank","status":"production-ready 24-page enhanced script"}]+[{"issue":n,"title":t,"status":"premise/outline from source export; not yet enhanced"} for n,t in [(3,"Blood Feud 311"),(4,"The Iron Worm"),(5,"Siege of the DMV"),(6,"War Council"),(7,"The Oracle's Couch"),(8,"Trial by Combat")]],"toneLock":"Bright, ordinary 2026 documentary-sitcom realism. Time refugees are routine civic reality. Vikings are intelligent and dignified; the comedy comes from incompatible systems."}
    (SHOW/"season_one_plan.json").write_text(json.dumps(plan,indent=2)+"\n")
    (SHOW/"pages_base.json").write_text("[]\n")
    for name in ["blocking","dialogue","direction","factions","lighting","mood","regions"]: (SHOW/f"{name}.json").write_text("{}\n")
    (SHOW/"negatives.json").write_text(json.dumps({"global":"no neo-noir, no cyberpunk, no dystopian grime, no stormy mythic lighting, no generic fantasy-Viking speech, no cigarette or ashtray, no character drift, no office or bank layout drift, no AI beige, no invented lettering"},indent=2)+"\n")
    pages=[make_page(i,s) for i,s in enumerate(P,1)]
    for a,b in ((1,6),(7,12),(13,18),(19,24)):
        raw=json.dumps(pages[a-1:b],ensure_ascii=False,separators=(",",":")).encode()
        enc=base64.b64encode(gzip.compress(raw,mtime=0)).decode()
        (SHOW/f"encoded/pages_e02_p{a:02d}_p{b:02d}.json.gzb64").write_text(enc+"\n")
    print(f"Built {len(pages)} pages, {sum(p['panelCount'] for p in pages)} panels, {sum(len(p['dialogueInline']) for p in pages)} lettering entries")

if __name__ == "__main__": main()
