# THINKING.md

## 1. Understand the user

**Who they are.** A shop-floor supervisor in a manufacturing plant. They run a line or a shift, look after operators and machines, and decide things like "can this machine keep running?" and "do we accept this lot?". They are on their feet, often at the machine, using a phone or tablet, sometimes with gloves on and a noisy background. They know the shop floor well, but they are not document experts.

**What they are trying to do.** Get a quick, reliable answer during the shift, such as:

- what an alarm code means and what the operator should do
- what a tolerance or limit is
- whether to accept or reject an incoming lot
- who is allowed to do a safety-related step (for example, removing a lockout lock)

**What frustrates them today.**

- The answer is somewhere in hundreds of PDFs and nobody knows which one.
- Old printed copies are still around, so they can't be sure they have the current revision.
- They interrupt a colleague, the maintenance team or the safety officer, who may be busy or may remember it wrong.
- A wrong answer is expensive: scrap, downtime, or a safety risk.

**Assumptions I made** (I have not worked in a plant, so these are assumptions, not facts):

- Supervisors prefer a short answer with the source over a long explanation.
- They would rather see "I don't know" than a confident wrong answer.
- Phone use is the norm, and Wi-Fi coverage on the floor is good enough for a web app.
- Documents have owners and revisions, and the current revision is the one that counts.
- Some answers (lockout/tagout, energy isolation) are safety-critical and should never be treated casually.

## 2. User journey

**Steps**

1. A machine shows an alarm, or an incoming lot arrives, and the supervisor needs a rule or a number.
2. They open the copilot on their phone (same Wi-Fi) and see sample questions plus a text box.
3. They type or tap a question in plain words.
4. The app searches the documents and returns a short answer.
5. They check the source: document number, revision, section and page. They can open the exact text or the PDF page.
6. If the answer is safety-related, they see a warning to confirm with the Safety Officer or shift supervisor.
7. They act, or escalate if the answer is "not in the documents". The app then tells them to ask the shift supervisor or the document owner.

**What could go wrong**

- **Wrong answer stated confidently.** For example, the lot question: the sampling rule applies to defects found in the inspected samples, but the question said "a lot has one minor defect", and the answer did not point out the difference.
- **Question not covered.** The app must say "not in the documents" instead of guessing.
- **Outdated document.** Rev 03 and Rev 04 of the inspection SOP give different sampling numbers.
- **Wrong source shown.** The answer may be right, but the passage shown may not support it.
- **Slow or failing answer.** The hosted LLM can time out or hit a quota, and a supervisor will not wait.
- **No connection.** Poor Wi-Fi, especially in dead spots near heavy machinery, means no answer at all.
- **Vague question.** "What is the limit?" with no machine named.
- **Too long to use mid-task.** A five-step lockout procedure on a small screen is hard to read when the supervisor is standing at a blinking machine.
- **Over-trust.** A supervisor may stop checking the source because the app is usually right.

## 3. AI challenge

**How I did it.** I pasted my draft of sections 1 and 2 into a chat with Claude (an AI assistant from Anthropic) and asked for an AI challenge: a critique from a skeptical shop-floor supervisor and from a skeptical product manager. The excerpts below are from that reply.

**Key excerpts**

> **Supervisor:** "I won't type a question on a phone while an alarm is blinking. I'm at the machine, hands busy, and I want to enter AL-104 and get two lines back. Make the first line of the answer the action, and keep the rest short."

> **Supervisor:** "The Wi-Fi near the presses is bad. You assumed good coverage. What happens to me when there is no signal?"

> **Supervisor:** "'Not in the documents' leaves me stuck. Then what do I do? Tell me who to ask."

> **Product manager:** "Your app is itself an uncontrolled copy. Every page says 'Uncontrolled copy when printed. Refer to QMS for the latest version.' A copy of the PDFs inside your app has the same problem, and it can go stale the day Rev 05 is released."

> **Product manager:** "Your own example says the app should ask a question. In the lot example the answer assumed the defect was found in the inspected samples. A good tool would ask 'Was that defect found in the 13 sampled pieces?' before answering."

> **Product manager:** "A banner is not a safeguard. The safety warning appears on every lockout answer, and people stop noticing warnings that always show."

**Reflection**

- **What I agreed with:**
  - The "uncontrolled copy" point. My version note only knows about the files in the data folder, so the app can itself go out of date. I added this to the limits in section 4 and to the document-control item in section 5.
  - The clarifying-question point. The 120-piece lot answer was a real example of the app sounding sure about something the question left open. I added it to "What I would build next".
  - Answer length. A short, action-first answer matters more on a phone than I had planned for. I added it to "What I would build next" and to the journey.
- **What I disagreed with, or kept:**
  - Offline mode and voice input are good ideas, but they do not fit a 5 to 6 hour build, so they are in "What I would build next" and not in the app.
  - On the safety banner, I agree that people can ignore a warning that always shows, and I have no evidence yet that it changes behaviour. I kept it because it costs almost nothing and the lockout answers are the riskiest ones. A real test would measure whether it changes what people do.
  - The critique pointed out that operators, QC inspectors and maintenance technicians ask different questions. I kept the supervisor as the user, as the brief asks, and listed the other roles as something to ask the customer about.
- **What I changed:** I changed the journey and this document: added the "too long mid-task" and dead-spot failure points, made the "not in the documents" step say who to ask, and wrote the new limits and next steps. I did not change the app code because of this critique. Those items are listed in section 5.

## 4. The improvement I added, and why

**What it is.** Two related features:

1. **Version awareness.** The app searches only the latest revision of each document. When an answer comes from a document that also has an older revision, a note says which revision was used and that the other is superseded.
2. **Safety flag.** Answers from the lockout/tagout procedure, or that involve energy isolation, show a "Safety step" warning telling the person to confirm with the Safety Officer or shift supervisor before acting.

**Why I chose it.** The sample documents show the two ways an answer can do real harm:

- QC-SOP-014 exists as Rev 03 and Rev 04, and they disagree. Rev 03 says to take 5 samples from every lot. Rev 04 uses a plan based on lot size. A supervisor following the old revision inspects the wrong number of pieces. Every page also says "Uncontrolled copy when printed", so old copies are a known risk in this plant.
- The lockout procedure has a general rule (each person removes only their own lock) and an exception for absent owners. A half-correct answer here can put a person at risk.

A wrong answer on a quality check is costly. A wrong answer on a lockout can injure someone. So the improvement targets those two cases.

**How I checked it.** Asking "A lot of 120 pieces has one minor defect" returns reject, from Rev 04 (13 samples, reject on 1 or more minor defects), with a note that Rev 03 is superseded. Asking who can remove a lockout lock returns the rule and the exception, from both sections, with the safety warning.

**Limits.**

- The safety flag is rule based (the SAF document, plus keywords such as lockout and isolate). It can miss a safety-related question phrased differently, so it is a nudge and not a guarantee. A warning that shows on every lockout answer may also get ignored.
- The version note only covers revisions that are present in the data folder. The app is itself a copy of the PDFs, so if the plant releases a new revision, the app is wrong until someone updates the folder.

## 5. Final reflection

### What I would build next

1. **Hybrid retrieval.** Exact matching for codes like AL-104 and BH-220, plus meaning-based matching for questions worded differently from the document (for example "how thick can the housing be" for a tolerance). I would test both against a question set and keep the combination that misses fewer.
2. **A proper test set.** I tuned on about eight questions. I would collect 30 to 50 real supervisor questions, mark the right sections, and measure accuracy and false "not found" rates before changing anything.
3. **Complete sources.** For the spindle runout question the answer was right, but the source list showed the limit and not the maintenance schedule where "monthly, by the maintenance technician" is written. I would retrieve and show every section that supports the answer.
4. **Short, action-first answers and clarifying questions.** Put the action in the first line, keep the rest short, and ask a question back when the rule depends on a detail the question does not give (for example, "Was that defect found in the 13 sampled pieces?").
5. **Document control.** Read revision status from the plant's document system instead of from files in a folder, so the app cannot quietly go out of date.
6. **Shop-floor usability.** Handling of weak signal, voice input for gloved hands, local languages, a "this answer was wrong" button that logs the question for review, and a "not found" message that points to the right document owner.

### What I am unsure about

- Whether the heading detection (bold, a certain font size, a leading number) works across hundreds of PDFs from different authors, and whether scanned PDFs need OCR.
- The "not found" threshold. A score cutoff catches clearly unrelated questions, but a question like "what PPE is needed for lockout" shares words with real sections and gets past it. Only the model's own judgement stopped that one, so I would not trust one safeguard alone.
- The model can sound more certain than a question allows. The 120-piece lot answer said "reject" without pointing out that the rule applies to defects found in the 13 inspected samples, not the whole lot.
- Whether it is acceptable to send plant documents to a hosted model.

### What I would ask the customer

1. What do supervisors ask most today? Can I see a sample of real questions?
2. Which documents are controlled, and how does a supervisor know which revision is current?
3. Does the plant's document system have an API for revisions and effective dates?
4. Are the PDFs digital or scanned? How many are there and how often do they change?
5. Can documents and questions leave the plant network, or must everything run locally?
6. What does a wrong answer cost, and who is accountable for safety content? Should the app answer safety questions or only point to the document?
7. What devices and Wi-Fi coverage exist on the floor? Which languages do supervisors use?
8. Do you need logins and an audit trail of who asked what?
9. Besides supervisors, do operators, QC inspectors and maintenance technicians need this too? Their questions differ.

### Challenges and how I handled them

- **Splitting the PDFs.** Cutting by page split the lock-removal rule in two, so one half had the rule and the other half had the exception. Tables came out as one cell per line. Bold text inside body paragraphs looked like a heading. I chunked by numbered section, detected headings by font size and bold together with the leading number, joined table cells that share a line into rows, and kept sections whole across page breaks.
- **Two conflicting revisions.** I marked the highest revision of each document as current, searched only current chunks, and added the version note.
- **Knowing when to say "not found".** I used a score threshold first, then the model's own "found: false". I tested with a spindle-speed question and a PPE question that the documents do not answer.
- **The LLM model name.** The model list showed `gemini-2.5-flash`, but calling it returned a 404 saying it was no longer available to new users. A raw request showed the real message, and I switched to a model Google recommended. I now check the model before testing and recording, and I note the model name in the README.
- **Set up.** Python 3.14 is very new, shadcn created a folder literally named `@` because the path alias was not set up yet, and a deprecated `baseUrl` option broke the build. I fixed each by reading the exact error.

### Biggest challenge: opening the app from a phone

- Runs on the laptop and can be opened from a phone. For my demo I used VS Code port forwarding so the phone could reach it
