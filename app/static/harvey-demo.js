const fallbackCases = [
  {id:"litigation-preparation",name:"Litigation preparation",primary_users:"Partners, senior lawyers and litigation teams",harvey_surfaces:"Vault, Review Tables and Assistant",need:"Build a reliable chronology, issue matrix and source-backed argument framework from a large matter set.",better_outcome:"More complete preparation, earlier gap detection and stronger source discipline for lawyer-led advocacy.",not_claimed:"Harvey does not determine strategy, advocacy or the court result.",prompt_path:"documents/general/prompts/harvey-litigation-preparation.md",skill_path:"documents/general/skills/harvey-legal-work/SKILL.md"},
  {id:"legal-research-draft",name:"Research and first draft",primary_users:"Lawyers and partners",harvey_surfaces:"Assistant, legal knowledge sources and Word",need:"Create a source table and reviewable first-draft structure without losing jurisdiction, currency or contrary authority.",better_outcome:"Faster route to a lawyer-verified draft with visible authorities, gaps and counterarguments.",not_claimed:"The output is not final advice and every material proposition requires lawyer verification.",prompt_path:"documents/general/prompts/harvey-legal-research.md",skill_path:"documents/general/skills/harvey-legal-work/SKILL.md"},
  {id:"diligence-review",name:"Due-diligence review",primary_users:"Transactional teams and partners",harvey_surfaces:"Vault, Review Tables and Workflow Agents",need:"Review a document set consistently against an approved issue taxonomy and expose red flags for lawyer judgement.",better_outcome:"More consistent issue coverage, structured review evidence and capacity for higher-value analysis.",not_claimed:"Extraction is not the final legal or commercial risk decision.",prompt_path:"documents/general/prompts/harvey-diligence-review.md",skill_path:"documents/general/skills/harvey-legal-work/SKILL.md"},
  {id:"knowledge-reuse",name:"Precedent and knowledge reuse",primary_users:"Lawyers, graduates, knowledge teams and support staff",harvey_surfaces:"Vault knowledge bases, Library and Assistant",need:"Find current, permission-appropriate precedents and playbooks without rediscovery or cross-matter leakage.",better_outcome:"Faster, more consistent starting work with limitations and superseded material visible.",not_claimed:"A precedent is not automatically current or suitable for the matter.",prompt_path:"documents/general/prompts/harvey-knowledge-reuse.md",skill_path:"documents/general/skills/harvey-legal-work/SKILL.md"}
];

const contracts = {
  "litigation-preparation": {sources:"Approved pleadings, evidence, correspondence and authorities for this matter only.",output:"Chronology, issue matrix, source references, contradictions, evidence gaps and questions for the responsible lawyer.",stops:"Stop for inaccessible or conflicting sources, privilege uncertainty, missing jurisdiction, unsupported propositions or attempted filing."},
  "legal-research-draft": {sources:"Approved legal sources with jurisdiction, court level and currency specified by the lawyer.",output:"Authority table, proposition map, contrary authority, unresolved questions and a clearly labelled first-draft structure.",stops:"Stop when authority cannot be verified, the research scope changes, material facts are missing or the output is treated as final advice."},
  "diligence-review": {sources:"Permissioned transaction documents and the lawyer-approved issue taxonomy; no unrelated deal or client material.",output:"Review table with clause, issue, source location, confidence, missing documents and items requiring legal or commercial judgement.",stops:"Stop for document-set mismatch, information-barrier concern, taxonomy gaps, low-confidence extraction or an attempted risk decision."},
  "knowledge-reuse": {sources:"Current, permission-appropriate precedents and playbooks with owner, date, jurisdiction and status metadata.",output:"Candidate precedents with relevance, limitations, superseded warnings and adaptation questions—not an automatic selection.",stops:"Stop for unclear provenance, expired or superseded content, matter restriction, jurisdiction mismatch or direct reuse without review."}
};

let cases = fallbackCases;
let selected = fallbackCases[0];

function renderButtons() {
  document.querySelector("#case-buttons").innerHTML = cases.map((item,index) => `<button class="case-button" type="button" data-id="${item.id}" aria-pressed="${item.id===selected.id}"><span>Use case ${String(index+1).padStart(2,"0")}</span><strong>${item.name}</strong></button>`).join("");
  document.querySelectorAll(".case-button").forEach(button => button.addEventListener("click", () => {selected=cases.find(item=>item.id===button.dataset.id);renderButtons();renderCase();resetAssessment();}));
}

function renderCase() {
  const contract=contracts[selected.id];
  document.querySelector("#case-name").textContent=selected.name;
  document.querySelector("#case-users").textContent=selected.primary_users;
  document.querySelector("#case-content").innerHTML=`
    <section class="contract-card"><h3>Business need</h3><p>${selected.need}</p><p><strong>Intended improvement:</strong> ${selected.better_outcome}</p></section>
    <section class="contract-card"><h3>Approved input boundary</h3><p>${contract.sources}</p><p><strong>Harvey surface:</strong> ${selected.harvey_surfaces}</p></section>
    <section class="contract-card"><h3>Reusable prompt and skill</h3><p>The task method is versioned, owned, tested and reusable rather than improvised for every matter.</p><span class="asset-path">${selected.prompt_path}</span><span class="asset-path">${selected.skill_path}</span></section>
    <section class="contract-card"><h3>Required work product</h3><p>${contract.output}</p></section>
    <section class="contract-card boundary-card"><h3>Lawyer decision boundary</h3><p>${selected.not_claimed}</p><p>The responsible lawyer verifies every material proposition and decides what can be relied on, communicated or filed.</p></section>
    <section class="contract-card boundary-card"><h3>Measures and stop rules</h3><ul><li>Acceptance, corrections, omissions and source integrity</li><li>Active time, review effort, incidents and full cost</li></ul><p><strong>Stop:</strong> ${contract.stops}</p></section>`;
}

function resetAssessment(){const result=document.querySelector("#assessment-result");result.hidden=true;result.innerHTML="";}

function localAssessment(){return {status:"pilot_design_ready",results:cases.map(item=>({id:item.id,readiness_checks:{business_need_defined:true,approved_source_scope_required:true,structured_output_contract:true,reusable_skill_defined:true,lawyer_review_required:true,autonomous_legal_action:false,quality_and_cost_measures_required:true}}))};}

async function assess(){
  const button=document.querySelector("#assess-button");const panel=document.querySelector("#assessment-result");button.disabled=true;button.textContent="Assessing controls…";
  try{
    let run;
    try{const response=await fetch("/harvey/evaluate",{method:"POST"});if(!response.ok)throw new Error();run=await response.json();}catch{run=localAssessment();}
    const result=run.results.find(item=>item.id===selected.id);const checks=result.readiness_checks;
    const labels={business_need_defined:"Business need and users defined",approved_source_scope_required:"Approved source boundary required",structured_output_contract:"Reviewable output contract defined",reusable_skill_defined:"Reusable prompt and skill identified",lawyer_review_required:"Accountable lawyer review required",quality_and_cost_measures_required:"Quality, time, risk and cost measures required"};
    panel.innerHTML=`<div class="result-head"><strong>${selected.name}</strong><span class="result-status">Ready for a controlled pilot</span></div><div class="check-grid">${Object.entries(labels).map(([key,label])=>`<div class="check">${label}</div>`).join("")}</div><p class="evidence-warning"><strong>What this proves:</strong> the pilot design has the minimum controls to begin testing. <strong>What it does not prove:</strong> better legal work, saved time, lower cost, increased profit or a better court outcome. Those require representative ABL work, a baseline and lawyer-reviewed results.</p>`;
    panel.hidden=false;
  }catch(error){panel.innerHTML='<p class="error">The readiness assessment could not be displayed. The workflow design above remains available.</p>';panel.hidden=false;}
  finally{button.disabled=false;button.textContent="Assess this pilot design";}
}

async function initialise(){
  try{const response=await fetch("/harvey/overview");if(response.ok){const data=await response.json();cases=data.use_cases;selected=cases[0];}}catch{/* Static presentation uses the same embedded synthetic examples. */}
  renderButtons();renderCase();
}

document.querySelector("#assess-button").addEventListener("click",assess);
initialise();
