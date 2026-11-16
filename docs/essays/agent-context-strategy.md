---
type: essay
title: "Agent context strategy: extraction, memory and enrichment"
description: What to extract from coding-agent sessions and meeting notes, and how to maintain, retrieve, enrich and evaluate that context for coding, SRE and enterprise workflow agents.
timestamp: 2026-11-16T00:00:00-08:00
---

# Agent context strategy: extraction, memory and enrichment

This document covers prompt-based extraction and what to extract from coding sessions and meeting notes, distinguishing coding, SRE and personal enterprise responsibilities using the assigned task and procedure applicability.

## 1. The central question

The central question is what useful context to extract from:

1. Coding-agent sessions in a Git superproject.
2. Meeting notes: design discussions, standups and sprint planning.

The consumers are a coding agent and a personal agent handling enterprise work such as security tickets, security or access intake portals and internal runbooks.

The immediate deliverable is trustworthy, actionable context. A graph server or specialized memory framework is a separate implementation question.

## 2. The prompt-based direction

To avoid depending on abandoned research projects, keep the architecture independent of a memory framework: use a versioned extraction prompt and JSON schema, SQLite for retrieval, an LLM for consolidation, and Inspect AI for evaluation.

This places original transcripts in GCS, structured extracted memory in SQLite, and retrieval in the coding-agent workflow. Hindsight is a replaceable component to test against that baseline, rather than a required dependency.

This is an architectural recommendation, not a finalized JSON schema.

For project-specific extraction assignments, use research agents to find sessions, reconcile evidence and check artifacts, beyond simply storing extracted facts.

## 3. Seven categories to extract from coding-agent sessions

| Group | Category | What the record should preserve |
| --- | --- | --- |
| Knowledge | Project knowledge | Architecture, codebase, dependencies, conventions, artifact identities and established findings, including negative results. |
| Knowledge | Decisions and constraints | What was decided, why, requirements and rejected alternatives. Distinguish owner decisions from agent proposals. |
| Experience | Successful strategies | What worked, for which task, under what conditions and with what verification. |
| Experience | Failures and recoveries | Intended result, observed failure, suspected or unknown cause, attempted fixes and the demonstrated rerun outcome. |
| Experience | User steering | Corrections, rejected approaches, preferences and goal clarification. Separate lasting rules from choices made for one run. |
| Experience | Agent behavior patterns | Recurring mistakes such as goal substitution, premature completion and unsupported assumptions, supported by independent occurrences and relevant counterexamples. |
| Continuity | Unresolved state | Open work, blockers, hypotheses, incomplete experiments and proposed next steps, dated and reconciled against later outcomes. |

The extraction should distinguish successful execution from a successful outcome. Examples include training loss versus actual model quality, simulated tests versus deployed use, and a completed render versus a satisfying creative result.

## 4. What to extract from meeting notes

| Category | Information to preserve |
| --- | --- |
| Goals and acceptance criteria | Desired outcome, reason, success criteria and explicit exclusions. |
| Decisions and constraints | What was agreed, by whom, why, rejected alternatives and conditions of applicability. Keep proposals separate. |
| Ownership and commitments | Owners, accepted commitments, beneficiaries and deadlines. A request is not an accepted commitment. |
| Dependencies and blockers | What depends on what, who or what blocks progress and the event or evidence needed to unblock it. |
| Operating procedures | Trigger, prerequisites, required information/artifacts, submission route, approvers, escalation and completion evidence. |
| State changes and open questions | What changed, what remains unresolved and which earlier statements are superseded. Separate reported status from verified status. |
| Experience and corrections | Supported lessons, failures, corrections and changes for next time. |

These fit within the same knowledge/experience/continuity framework. Meeting notes make ownership, commitments and procedures particularly important; they do not require an unrelated memory system.

## 5. What coding, SRE and personal enterprise agents should receive

### 5.1 Route context by the work being performed

An agent should receive the applicable goals, facts, decisions, constraints, procedures and current state needed to complete its assigned task. Its role is a useful starting point for relevance. The actual task, affected service, environment, current status and source determine what it needs.

A procedure can be relevant to several agents. A coding agent assigned a deployment can need the operational runbook; an SRE agent implementing a patch can need repository build and test instructions. Preserve one source-backed procedure and retrieve the applicable detail for each assignment.

Relevant context does not itself grant permission to perform an action. Scope, access and authorization remain separate from the agent's role label.

### 5.2 Default context for each agent

| Agent or responsibility | Context it usually needs | Typical procedures |
| --- | --- | --- |
| Coding agent | Requirements, acceptance criteria, design rationale, affected code and interfaces, applicable dependencies, implementation constraints, current blockers and verification evidence. | Repository setup, approved dependencies, build/test/code generation, migrations, review and PR requirements. Deployment or intake procedures when those are assigned work. |
| SRE or operations agent | Service topology and dependencies, environment and version, relevant recent changes, runtime observations, monitoring, service objectives, incident history, access constraints and current operational state. | Diagnosis, incident response, escalation, deployment, health checks, rollback, recovery and post-change verification. Coding procedures when preparing a patch. |
| Enterprise workflow assistant, such as access or security intake | Purpose of the request, affected service/environment, applicable policy, required evidence, request owner, routing, approvers, prerequisites and actual request status. | Access/security requests, security intake submissions, evidence collection, submission, escalation and approval follow-up. Retrieve the technical context needed to prepare an accurate request. |
| Delivery or coordination assistant | Agreed scope, owners, accepted commitments, dependencies, deadlines, release gates, decisions and unresolved questions. | Handoffs, status reporting, dependency follow-up and coordination of approval or release work. Operational commands are relevant only if its assigned task includes executing them. |
| Other personal enterprise assistant | The employee or team task, applicable internal policy, required information, responsible contacts and current workflow state. | The specific internal runbook needed for that task. Unrelated engineering and operational procedures need not be loaded. |

These responsibilities can overlap or be combined in one agent. They describe useful context, not a requirement to create five separate agents.

### 5.3 Does a coding agent need internal procedures?

**Yes. “Internal procedures” is too broad to reserve for a personal enterprise agent.** Distinguish the type of procedure and the current task.

| Procedure | What the coding agent needs | What other agents may need |
| --- | --- | --- |
| Repository setup, build, tests, code generation and approved package sources | Applicable steps and prerequisites needed to implement and verify its change. | SRE needs these when reproducing a problem or preparing a patch. |
| PR, CI and engineering review requirements | Required checks, review conditions, artifacts and completion evidence. | SRE needs release readiness; coordination agents need blocking reviews and status. |
| Deployment, migration, health checks and rollback | Full applicable procedure when assigned to execute or prepare that change. Otherwise, constraints and handoff requirements that affect implementation. | SRE normally needs the current environment-specific execution and verification steps. |
| Security approval, access provisioning or security intake | Applicable engineering constraints, approval gate and technical evidence it must produce. Submission steps are also relevant if preparing or filing the request is part of its task. | The enterprise workflow assistant needs routing, required fields/attachments, approvers, status and follow-up steps. |
| Incident triage and escalation | Relevant evidence and constraints when investigating an incident. Full operational steps when incident handling is assigned. | SRE needs the applicable response procedure, escalation path, recovery conditions and verification. |
| Employee or team administration unrelated to the change | Usually unnecessary for the coding task. | The relevant personal enterprise assistant needs the applicable administrative procedure. |

Load enough detail to carry out the assigned work correctly. A one-line summary is insufficient when the agent owns execution; the entire runbook is unnecessary when it only needs to know a gate and produce a handoff artifact.

Enterprise constraints matter to coding, while portal navigation and follow-up logistics depend on the assignment. Recognize engineering and operational procedures explicitly.

### 5.4 What to preserve when extracting a procedure

Extend the existing procedure category with the detail needed to select and apply it correctly:

| Information | Why it matters |
| --- | --- |
| Trigger and intended outcome | Establish when to use the procedure and what completion means. |
| Scope | Identify the service, repository, environment, version or class of work to which it applies. |
| Prerequisites and constraints | Preserve required access, approvals, dependencies and conditions that must hold before execution. |
| Steps, required artifacts and completion checks | Let the assigned agent perform the work and verify the result. Keep submitted, approved and completed states distinct. |
| Execution owner and handoff | Identify who performs each part, who receives the output and what evidence the next actor needs. |
| Source, date/version and current status | Distinguish a current runbook or approved decision from a proposal, an old incident workaround or a superseded instruction. |

These are proposed extraction requirements, not a finalized JSON schema. Record unknown details as unknown. Do not invent approvers, procedures or commitments.

Candidate agent roles can help discovery, but should not be exclusive ownership tags. Select context using the current task and applicability. Enforce visibility through the actual access rules; relevance tags are not access control.

### 5.5 Example: one change, different useful context

Consider a hypothetical service integration that needs a code change, security approval and a controlled production rollout. These are illustrative responsibilities, not a prescribed approval process.

| Assigned work | Context to deliver | Output or evidence to hand over |
| --- | --- | --- |
| Coding agent implements the integration | Requirements, compatibility constraints, repository procedures, tests, approval gate and required technical evidence. | Reviewed code, test results, the requested technical diagram or other evidence, and migration/deployment notes where applicable. |
| Enterprise workflow assistant prepares the security request | Change purpose, affected service/environment, applicable intake procedure, required evidence, identified owner/approvers and current request status. | Prepared or submitted request as assigned, linked evidence and accurately recorded approval state. |
| SRE agent rolls out the approved change | Exact approved artifact, applicable approval evidence, environment state, rollout/migration procedure, health criteria and rollback instructions. | Deployment and verification results, observed issues and any recovery actions. |
| Coordination assistant tracks readiness | Owners, commitments, artifact links, dependencies, approval/deployment state and unresolved blockers. | An evidence-backed readiness/status update and the next required handoff. |

A submitted request is not approval. A passing code test is not production rollout evidence. An old incident fix is not automatically the current recovery procedure.

### 5.6 How the extraction prompt should change

Keep the seven extraction categories. Within project knowledge, decisions/constraints and unresolved state, make procedure applicability and handoffs explicit.

The proposed extension to the extraction instructions is:

- Extract relevant engineering, operational and enterprise workflow procedures wherever the source supplies them.
- Preserve their trigger, scope, prerequisites, steps, required evidence, owner, completion checks and source/status.
- Preserve the constraint that applies to the work separately from the steps for satisfying it, while keeping them linked by the affected task or service.
- Identify the responsibilities that may need the information, without making agent roles exclusive information silos.
- For each current assignment, select the applicable context and procedure detail; keep evidence of unresolved gates and handoffs.
- Do not infer authorization, policy approval, successful execution or completed outcomes from the existence of a procedure or a role label.

## 6. Evidence requirements of the extraction work

The extraction work involves investigation beyond summarizing a transcript:

- Discover relevant sessions, archives and handoffs.
- Identify duplicate exports and session continuations.
- Check claims against commits, tests and artifacts where available.
- Distinguish user decisions from assistant suggestions.
- Reconcile historical blockers with later outcomes.
- Support recurring behavior claims with independent events.
- Produce evidence-backed category reports and a source inventory.

Preserve the source, scope, date/status and applicability of a decision or lesson. Do not upgrade a reported claim into a verified outcome.

## 7. Graphs and explicit relationships

The coding agent needs to understand connections relevant to its task, but does not inherently need separately extracted graph records. Current dependencies can often be investigated in current code/configuration. Historical meetings are especially useful for rationale and constraints that the code does not explain.

The requirement is to preserve **what each decision, constraint or lesson applies to**. A graph becomes useful only if repeatedly reconstructing cross-repository, cross-team or historical connections becomes a demonstrated problem.

## 8. How supporting methods shape extraction

Use the methods below for specific jobs in the extraction process. The organizing structure remains knowledge, experience and continuity; the methods help preserve the meaning and evidence within those categories.

| Method or approach | What to use | Boundary |
| --- | --- | --- |
| GADR-style decision extraction and critique | Identify architectural decisions, their context, alternatives, rationale and consequences; check the draft against the original discussion. GADR concerns gathering architecture decision records from meeting transcriptions. | Design decisions are one part of meeting extraction. Standups, commitments and procedures need their own records. External research cannot establish what the meeting agreed. |
| EARS — Easy Approach to Requirements Syntax | Optionally express an established behavioral requirement as a condition or trigger and the required system response. | Preserve the original statement, authority and agreement status. Clear wording does not establish that a requirement was approved. |
| BDI — beliefs, desires and intentions | Separate what someone believes or reports, what outcome they want and what they actually commit to doing. | A reported belief can be wrong; a goal may have no owner; a commitment does not grant permission. Simple typed records can preserve these distinctions. |
| Long-horizon prompting | Recover the task's completion contract: success criteria, outcomes that do not count, required evidence, handoff obligations and stop conditions. Use applicable established requirements when preparing the next task brief. | An extractor records the historical contract. Newly suggested requirements stay identifiable as proposals. A prompt does not enforce runtime permissions or spending limits. |
| Context Engineering | Preserve source recovery, applicability and the distinction between stored history and the context selected for current work. | Sections 11–16 define the lifetime, reconciliation, retrieval, enrichment and evaluation strategy. |
| Cognee, Mem0 or Hindsight | Consider a replaceable memory engine for organizing and retrieving accumulated context. Project-specific extraction instructions can work with a framework. | No engine is required by this strategy or established as the winner. Evaluate fit, accuracy, cost and operating effort. |
| MASS — Multi-Agent Self-Supervision | Retain useful workflow experience: what each worker received, returned, checked and handed onward. | The full workflow-optimization and supervised fine-tuning loop is a separate experiment. It is not a prerequisite for extracting context. |

These choices do not require adding a graph service, formal cognitive runtime or new fleet of agents. A research agent can perform discovery, extraction and critique in an existing workflow. The work should be divided only where that division improves execution or verification.

For example, an agreed compatibility requirement could be expressed in EARS form as:

> While the warehouse consumer migration remains unverified, the integration shall preserve the existing parcel event format.

The original statement and its evidence must remain available. The normalized sentence should not erase who decided it, which integration it concerns or the event that would end its applicability.

## 9. Worked example: source evidence to usable agent context

### 9.1 Subject, evidence and requested use

Everything in this example is fictional. Dates, people, identifiers, procedures and statements illustrate the design; they are not actual enterprise policy or records.

**Subject:** a shipping-label provider integration in the parcel service.

**Requested use:** support implementation, preparation of a security request and eventual production rollout.

**Evidence:** a design meeting, a published intake procedure, a coding session, a request-status record and a rollout runbook. These are the materials being investigated. The derived context describes the integration and its constraints; it does not silently rewrite the sources.

Assume the investigator has the following evidence as of November 13, 2026:

| Source | What it actually establishes |
| --- | --- |
| E1 — Design meeting, November 10, decision and commitment passages | The technical owner decides to preserve the existing parcel event format until the warehouse consumer migration is verified. Local implementation with a mock provider may proceed. Production provider use requires the security approval described by the applicable intake procedure. Priya accepts responsibility for preparing the request after receiving the technical evidence. |
| E2 — Current published production-provider intake procedure, version 4, effective November 11 | A request requires a data-flow diagram and runtime-identity profile. Submission and approval are separate states. The procedure identifies the approval route. |
| E3 — Coding session, November 12, completion statement, tool results and owner correction | The agent says the integration is complete. Available results show passing unit tests using a mock provider. No live-provider verification is present in the supplied evidence. The owner corrects the completion statement and asks for separate implementation and production-readiness status. |
| E4 — Security-request status record, November 13 | Request SEC-123 is submitted. The supplied record contains no approval decision. |
| E5 — Current parcel-service rollout runbook, version 3 | Production rollout requires the applicable approval, an exact release artifact, environment checks, rollout verification and rollback preparation. The procedure supplies the detailed execution steps. |

The investigator should report evidence limitations. An absent live-provider test in the supplied material establishes a verification gap; it does not by itself prove that the integration is broken. A submitted request with no approval evidence must not become an approved request in the derived context.

### 9.2 The extracted records

The identifiers below are illustrative report references, not a finalized database schema.

| Record | Category | Extracted content and qualification |
| --- | --- | --- |
| R1 | Decisions and constraints | Preserve the parcel event format until warehouse consumer migration is verified. Scope: this integration and its event consumers. Source: E1, technical-owner decision. No evidence ending the condition is supplied. |
| R2 | Project knowledge / procedure | Production-provider intake requires the diagram and runtime-identity profile, with submission and approval recorded separately. Source: E2, version 4. Preserve the actual route and prerequisites from the procedure. |
| R3 | Successful strategies / verification | Mock-based unit tests passed for the implementation covered by E3. This supports a bounded implementation result; it provides no demonstrated live-provider outcome. |
| R4 | Failure and user steering | The completion claim in E3 exceeded the available verification. The owner requested separate implementation and production-readiness status. This is one supported occurrence, not evidence of a recurring behavior pattern. |
| R5 | Unresolved state | SEC-123 is submitted as of November 13. Production approval is unverified in the supplied evidence. Source: E4. Later status evidence must be reconciled before relying on this state. |
| R6 | Ownership and commitment | Priya accepted the request-preparation responsibility, conditional on receiving the technical evidence. Source: E1. Preserve the accepted assignment without inventing a deadline. |
| R7 | Procedure and handoff | An eventual rollout needs an exact release artifact, applicable approval and the environment-specific execution, verification and rollback steps. Source: E5. The runbook is evidence about the procedure; it is not evidence that rollout occurred. |

A useful extraction also records the available code revision, artifact identity and environment. Where these are absent, mark them unknown rather than assigning plausible values.

The record set supports several conclusions with different strength: a technical decision was made; particular tests passed; a request was submitted; live-provider behavior and production approval remain unverified. Those distinctions should survive into the consumer's brief.

### 9.3 The context each assignment receives

The briefs below are derived from the same record set. A source reference such as E2 means the agent can retrieve the exact relevant procedure, rather than depending on the short description alone.

**Coding assignment: implement and verify the integration**

> Implement the shipping-label adapter for the parcel service. Preserve the current event format while the warehouse migration condition in R1 remains unresolved. Local mock-based implementation may proceed.
>
> Use the applicable repository setup, build and test procedures. Report the revision and what each verification actually exercised. Passing mock tests establish the tested implementation behavior; state separately what has been checked against the real provider.
>
> Produce the diagram and runtime-identity profile required by E2. Keep production access and rollout status explicit. The supplied record for SEC-123 shows submission, with approval unverified.

This brief gives the coding agent both technical work and the enterprise constraint affecting that work. The full intake-navigation procedure becomes relevant if the assignment expands to preparing the request itself.

**Enterprise assignment: prepare or track the security request**

> Use intake procedure E2, version 4, for this production-provider request. Collect the diagram and runtime-identity profile, identify any missing information and follow the procedure's actual routing.
>
> Priya accepted responsibility for preparation. SEC-123 is recorded as submitted as of November 13. Check the current request record when acting; report submission, approval and completion as distinct states. Retrieve enough implementation context to describe the data flow and runtime identity accurately.

The enterprise assistant receives the procedure detail needed for its work, together with the technical facts needed to avoid an inaccurate submission.

**SRE assignment: assess rollout readiness**

> Assess readiness using the exact release artifact, current environment state, applicable approval evidence and rollout runbook E5. The supplied evidence contains neither an identified approved release artifact nor a verified approval decision; establish those facts before execution.
>
> Preserve the event-format constraint in R1. When assigned rollout execution, retrieve the complete applicable rollout, health-verification and rollback steps. Report observed deployment results separately from implementation tests and request status.

This brief does not manufacture a production-ready conclusion from passing unit tests. It identifies the evidence and procedure needed to assess readiness.

**Coordination assignment: report the current handoff**

> Report the verified implementation result, the technical artifacts needed for intake, the accepted request owner, SEC-123's current status and unresolved rollout conditions. Distinguish completed work, reported progress and independently verified readiness.

### 9.4 What the example demonstrates

The immediate usable outputs are an evidence inventory, qualified records and task-relevant briefs. A graph database is not needed to preserve the decision's affected component, condition, source and status.

The example also makes domain meaning explicit. “Implementation tested,” “request submitted,” “production approved” and “rollout verified” refer to different outcomes. The extractor should preserve the definitions supplied by the actual project and process, rather than allow one vague “complete” label to cover them all.

## 10. Scope choices and their reasons

### 10.1 Included in the baseline

The baseline includes project-specific research prompts, a versioned record format, the seven session categories, meeting-derived procedures and commitments, evidence-backed status, applicability, source recovery and task-based delivery. Original sources remain available through GCS; SQLite/FTS5 provides the initial indexing and retrieval foundation. Inspect AI provides the evaluation route.

The format and examples in this guide describe required information and behavior. The exact JSON schema, scheduling and acceptance thresholds still need to be specified for the implementation. No empirical quality or cost improvement is claimed here.

### 10.2 Excluded or deferred

| Item | Position | Reason |
| --- | --- | --- |
| Graph infrastructure and mandatory separately extracted edges | Defer from the baseline | Current code/configuration can establish many technical dependencies; historical rationale can be preserved in scoped records. A separately maintained dependency map may duplicate evidence and become stale. |
| Dedicated knowledge-graph construction architectures | Exclude from this scope | Their graph-building topology, construction pipeline and approval stages add responsibilities without an established need in the extraction task. |
| Full spec-driven development (SDD) workflow | Exclude from this scope | Constitution files, branch ceremonies and repeated interviews concern the broader development process. This guide supplies context to existing workflows. |
| Formal BDI/RDF runtime | Exclude from the baseline | Ordinary records can preserve reports/beliefs, goals and commitments. No formal ontology-reasoning requirement has been established. |
| Full GADR stack and ADRs for every meeting | Exclude | Borrow decision extraction and critique. Standups, planning, commitments and operating procedures also contain useful non-ADR material. |
| Full MASS workflow optimization and SFT | Keep separate | It is an additional improvement/training experiment beyond extracting and maintaining useful context. |
| A required Cognee, Mem0 or Hindsight deployment | Leave undecided | A framework can support customized extraction. No winner has been demonstrated for this workload; judge accuracy, integration, cost and operating effort. |
| Google Knowledge Catalog deployment | Exclude from the baseline | Its enrichment principles can inform the workflow while the GCS/SQLite foundation remains in place. Product adoption is a separate enterprise decision. |
| Automatic edits to standing instructions, policies, runbooks, skills or model weights | Exclude from extraction | An observed event or proposed lesson does not authorize changing the rules or system governing future work. Suggested changes must remain explicit. |
| Permanent promotion of every observation or whole-history injection | Exclude | Preserve raw history and active continuity, while selecting applicable context and accounting for changing state. |
| A fixed fleet of agents for every responsibility | Exclude as a requirement | Coding, SRE, enterprise and enrichment describe work and context needs. Existing agents can combine responsibilities. |

### 10.3 What the graph decision means

A coding agent can need multi-hop reasoning. It may trace an API change through callers and consumers or connect a technical constraint with an external team's migration. Multi-hop reasoning, code-analysis tools and a graph database for historical memory are different choices.

The baseline decision is to preserve applicability and evidence in ordinary records and use current code/configuration where it is the appropriate source. It is not a conclusion that graphs are useless to coding agents.

Reconsider a graph when recurring cross-repository, ownership, approval or historical-impact questions are consistently difficult or unreliable with search and linked records. A concrete task set should establish whether graph-based retrieval improves accuracy or effort enough to justify maintaining the graph.

## 11. Give extracted records different lifetimes

The seven extraction categories describe what information means. They do not imply that every record should remain active for the same length of time. The strategy proposes three maintenance lifetimes, while retaining the original evidence behind all of them.

| Lifetime | Information it holds | How to maintain it |
| --- | --- | --- |
| Durable knowledge | Established architecture, approved decisions, standing constraints and applicable procedures. | Keep current until an authoritative change supersedes it or its documented ending condition makes it inapplicable. Preserve its scope and the earlier record. |
| Reusable experience | Successful approaches, demonstrated recoveries, corrections and recurring behavior supported by evidence. | Retain the conditions under which the experience applies. Reassess it when the code, environment or procedure changes. |
| Dated active continuity | Open tasks, temporary restrictions, pending approvals, blockers and unresolved hypotheses. | State when it was last checked, what would resolve it and whether it still affects the current assignment. |

These are maintenance choices within the existing categories, not three replacement taxonomies. A decision can remain durable while a blocker associated with it closes. An incident can produce a reusable recovery lesson while its immediate operational state becomes historical.

In the fictional shipping-label integration from section 9, the conditional requirement to preserve the parcel event format is durable knowledge. A demonstrated verification approach with its limits is reusable experience. The security request awaiting approval and the unverified warehouse migration are active continuity. Evidence that the migration condition has ended would change which tasks receive the compatibility constraint.

Temporary information should not disappear merely because it is unsuitable as a permanent rule. “The security portal is unavailable this afternoon” may still block today's submission. Preserve it as dated active state, then reconcile it when service returns. Do not promote it into the standing submission procedure.

## 12. Reconcile candidates before changing served context

An extraction produces candidate records. Before those candidates become context delivered to other agents, compare them with related existing records. Preserve the outcome of that comparison, including why a candidate made no change.

| Operation | When it applies | Shipping-label example |
| --- | --- | --- |
| Add | The candidate supplies genuinely new information. | An identified owner accepts responsibility for the production security request. |
| No-op | The same information already exists with adequate evidence and scope. | Another standup repeats that the request is awaiting approval. Record a fresh status observation if useful, without duplicating the standing requirement. |
| Merge | The candidate adds compatible detail. | The established intake procedure gains a confirmed attachment requirement. |
| Supersede | An authoritative change replaces an earlier applicable statement. | The responsible team replaces the old submission route with a new one. Mark the previous route as superseded and retain its history. |
| Version by scope or time | Both statements remain valid under different conditions. | Staging can use its approved test credentials while production credentials remain gated. Keep the distinction explicit. |

Recency alone does not decide authority. A recent agent summary does not override an approved decision. A procedure for one environment does not replace another environment's procedure. A suggestion remains a suggestion until the source establishes its acceptance.

When the evidence cannot settle a conflict, retain both claims with their sources and state what is unresolved. Do not manufacture a single current answer by averaging the wording or choosing whichever record sounds more confident.

Retain raw history independently of these operations. A compact current record can change while its original statement, supporting artifacts and supersession history remain recoverable. Reconciliation changes what is served as current context; it does not rewrite what happened.

## 13. Make context expandable and retrieve it at useful moments

Every served record should stand on its own. Name the affected service, environment and decision instead of relying on phrases such as “this integration” or “the issue above.” Include enough evidence and status for the reader to understand why the record matters.

Also preserve a precise recovery route to the original material: the source session or meeting, its relevant passage, and any supporting commit, test result or artifact. A source identifier without an available way to read it is insufficient. Label summaries and interpretations as derived context so the working agent can distinguish them from the source.

For the shipping-label integration, a short record might state that production access is awaiting security approval and identify the request's last verified state. The enterprise assistant can expand the intake procedure; the coding agent can expand the technical evidence requirements; the rollout owner can inspect the approval evidence when it becomes available.

The proposed retrieval default is to assemble context at the start of an assignment, then revisit it when the task, environment or relevant state changes. Repeated errors or contradictory evidence are additional reasons to search. This is a timing proposal, not a requirement to reload all history on every turn.

Keep the initial working context bounded around:

- The requested outcome and completion criteria.
- Applicable decisions, constraints and procedure steps.
- Current blockers and handoff obligations.
- Experience whose conditions match the present work.
- Pointers for expanding evidence when needed.

If an agent owns execution, supply the applicable steps and checks rather than only a procedure title. If it only needs to produce a handoff artifact, supply that obligation and the relevant conditions. Where filtering or compression omits detail, keep an explicit route to expand it; do not present a shortened result as proof that no other evidence exists.

## 14. Run goal-driven context enrichment

An enrichment agent investigates whether the context being delivered actually helps the consumer and proposes evidence-backed improvements. This is the workflow principle borrowed from Knowledge Catalog: use a defined goal and available evidence to improve the derived context for downstream work. It can be performed by the research or extraction agent already used for extraction, within the GCS/SQLite foundation; no additional permanent agent fleet or catalog deployment is required.

State the subject and intended outcome before investigating. In the shipping-label example, the goal is to give implementation and rollout tasks the current compatibility and approval conditions, together with the evidence required to interpret them. A larger quantity of extracted text is not the success criterion.

For each investigation, keep three things distinguishable: the subject being described, the evidence about that subject, and the derived context prepared for an agent. A service, its security request and a summary of that request are related, but they are not interchangeable evidence.

Start with a concrete failure or missed need. Extend the fictional example: suppose a later coding attempt changes the parcel event format while the warehouse migration is still unverified. Inspect the task, repository state, retrieved records and the exact context the agent received. Determine whether the compatibility requirement was missing, was delivered for the wrong component, had become stale, was expressed ambiguously, or was present and ignored. If the received context is unavailable, record that limitation instead of diagnosing the failure from the final answer alone.

Then investigate the authoritative sources and available execution evidence. Propose a bounded context change only when the evidence supports one. For example, a candidate may make R1's affected component and migration condition clearer, while preserving E1 as its source and stating whether the condition is resolved. It must not turn an unsupported guess about the implementation into an approved requirement. If clear, applicable context was already delivered, a context rewrite may not address the failure; record that result and investigate execution separately.

Keep proposed changes separate from the currently served records while they are evaluated. A draft correction, experimental summary or proposed procedure should not silently become current context merely because it was written to the same project folder.

Evaluate a candidate first on development cases where changes can be inspected and revised. Hold the consumer agent, starting repository, task inputs, tools, execution conditions and scoring criteria fixed as far as practical, varying the context change under examination. Record unavoidable differences. Use separate held-out tasks to check whether the change helps beyond the examples used to develop it; do not repeatedly tune against their answers.

After a supported change is incorporated, verify delivery as well as storage. Check that a matching assignment retrieves the intended current record, that its scope and evidence survive presentation, and that a superseded version is not still being injected. A corrected record that never reaches the working agent has not repaired the failure.

This responsibility concerns extracted records and their delivery. Any proposal to change model weights, standing agent instructions, harness behavior or policy should remain an explicit separate proposal with its own authorization and checks. Updating context must not silently introduce those changes. Delivering a source-backed requirement in the current task brief is part of context delivery; converting a suspected lesson into a permanent global instruction is a separate change.

## 15. Evaluate components and completed work

Good-looking records are insufficient evidence that the system works. Check individual stages, then check whether the same consumer completes representative tasks more reliably with the resulting context.

| Evaluation level | Acceptance example |
| --- | --- |
| Extraction | A meeting proposes a new provider, but never approves it. The output preserves the proposal and unresolved decision instead of reporting adoption. |
| Evidence preservation | The event-format requirement keeps its affected component and migration condition. Expanding the record retrieves E1 and any later evidence resolving the condition. |
| Reconciliation | Repeated wording does not create duplicate standing rules. Different staging and production conditions remain distinguishable. |
| Current-state handling | A submitted security request remains submitted until approval evidence exists. A later verified approval resolves the blocker without erasing its history. |
| Retrieval | The coding assignment receives the applicable event-format constraint. The intake assignment receives the submission steps. A rollout assignment receives the current approval state and execution procedure. |
| Delivery | After a correction, a matching task receives the corrected record rather than an older cached or previously assembled version. |
| Downstream task | Under matched conditions, the working agent meets the task's actual completion criteria, including compatibility and the required handoff evidence. |

Include cases the existing system already handles correctly. A context change that repairs a premature format change should also preserve a straightforward successful integration change and a correctly handled pending approval. Include a case where the warehouse migration is verified, so an ended restriction is not applied forever. These positive cases guard against replacing one mistake with another.

Measure the distinctions that matter to the stage being changed: missing or invented facts, lost conditions, wrong reconciliation decisions, irrelevant or absent retrieval, repeated user corrections and completed-task errors. Compare effort, latency and cost where they affect usefulness. More retrieved records, fewer questions or fewer tokens are not sufficient wins by themselves.

No performance gain or universal acceptance threshold is assumed here. The dataset, rubric and completion criteria should be stated for the actual experiment. Once those are fixed, compare the candidate with the existing context and retain enough evidence to explain the result.

## 16. Keep the operating choices explicit

The lifetimes, reconciliation operations and retrieval moments above are proposed defaults for making the extraction design usable. They are not a finalized storage schema or a claim that the system already implements them.

Capture evidence as work occurs. A reasonable default is to consolidate it at a completed handoff or another stable boundary, while retaining urgent changes as dated active state. The exact schedule depends on the workflow: an approval change needed for the next action cannot wait for a later archival pass. Whatever timing is chosen, keep candidate extraction, incorporation and actual delivery distinguishable so a failure can be located and corrected.
