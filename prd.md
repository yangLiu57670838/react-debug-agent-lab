# PRD: React Debug Agent Lab

**Repository:** `react-debug-agent-lab`
**Status:** Draft
**Timeline:** 1-week study, followed by the production plan in Section 16
**Stack:** React, FastAPI, LangChain, LangSmith, GitHub API, Docker, AWS

## 1. Summary

This project is a small exploratory study and working prototype. An AI agent receives a React error log or problem report, reads source code from GitHub, and returns the likely file, root cause and a suggested fix.

The study uses six hand-created test cases in one simple React app, and a person scores the results. It explores how different kinds of code context affect debugging quality, cost and speed. The agent always reads the deployed commit that produced the problem, so later code changes don't affect the results.

## 2. Research questions

1. **RQ1:** How does access to source code affect debugging compared with an error log alone?
2. **RQ2:** How does letting the agent explore the repository compare with giving it only the file named in the stack trace?
3. **RQ3:** What do the extra context and tool calls cost in tokens, money and latency?

## 3. Expected outcomes

Write these down before the main experiment starts. With six cases, the study can show whether the results appear consistent with them, but it can't confirm them.

- **E1:** Agents with source code access identify the correct file and root cause more often than the log-only condition.
- **E2:** Repository exploration performs better than the implicated-file condition when the root cause is outside the file named in the stack trace.
- **E3:** Repository access increases tokens, cost and latency.
- **E4:** Some agent runs will invent a bug for the false-alarm case.

## 4. Goals and non-goals

### Goals

- Create six reproducible React test cases with answers written in advance.
- Compare three context conditions using the same model and settings.
- Trace every run in LangSmith and store human scores.
- Deploy a working demo API to AWS.
- Publish the code, test cases, method and results.

### Non-goals for the one-week study

The long-term plan is in Section 16.

- Automatically merging, deploying or changing production code
- Supporting multiple repositories or languages
- Building a complete developer product
- Using customer data, personal data or private business logs
- Giving the scored runs a web search tool
- Proving that one condition is better in general

## 5. Experiment design

### Conditions

| ID | Condition | Context available to the agent |
|---|---|---|
| **C1** | Log only | Error log or problem report |
| **C2** | Implicated file | C1, plus the source file named in the stack trace at the deployed commit |
| **C3** | Repository exploration | C1, plus repository tools fixed to the deployed commit |

C2 is a simple non-agent baseline. If the input doesn't identify a source file, C2 receives only the log or report, and the run is flagged. Section 9 draws all three conditions as one graph: C1 and C2 take a single model step, and C3 loops through repository tools.

### Test cases

Use a demo copy of one simple React app, with one case of each type:

| ID | Type | Example | Input to the agent | Correct result |
|---|---|---|---|---|
| **B1** | React hook | Missing `useEffect` dependency causes stale data | Problem report and failing test output | Identify and fix the dependency |
| **B2** | Fetch error | Parsing an HTML error page as JSON | Captured error log | Check the response before parsing it |
| **B3** | Component | Reading `user.profile.name` when `profile` is missing | Captured error log | Handle the missing data |
| **B4** | Context API | Using a context outside its provider | Captured error log | Fix the provider setup, which is outside the file named in the stack trace |
| **B5** | Security | Rendering user input with `dangerouslySetInnerHTML` | Problem report and failing security test output | Remove the unsafe rendering or sanitize the input |
| **B6** | False alarm | Temporary network failure with no code bug | Captured error log | Report that no code bug was found and propose no code change |

For each case:

1. Create a commit containing the case, and record it as the deployed commit.
2. Reproduce the problem and save the real log, failing test output or problem report.
3. Write the correct file, root cause and acceptable fixes before running the agent.
4. Create a check that confirms the fix, using an automated test where possible or written manual steps otherwise.
5. Record whether the root cause is in the source file named in the stack trace.

Example record:

```json
{
  "case_id": "B3",
  "type": "component",
  "input": "TypeError: Cannot read properties of undefined...",
  "deployed_commit": "abc1234",
  "has_code_bug": true,
  "cause_in_stack_file": true,
  "expected_file": "src/components/Profile.jsx",
  "expected_cause": "user.profile can be undefined when the API omits it",
  "acceptable_fixes": ["Handle missing profile data before rendering"],
  "verification": "npm test -- Profile.test.jsx"
}
```

### Controls

- Use the same model, settings, system prompt and output format for every condition.
- Keep web search out of the 54 scored runs. Section 9 says where Tavily may be used.
- Limit each run to 8 tool calls.
- Run each case 3 times per condition, for 54 runs in total.
- Randomize the run order.
- Freeze the test cases, prompt, rubric and expected outcomes before the main run.
- Use 1 additional case to test the setup, and keep it out of the final results.
- Record the exact model name, code version and run date.

## 6. Human evaluation

Score each run from 0 to 2 on each criterion, for a total out of 8:

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| **File** | Wrong | Related file | Correct |
| **Root cause** | Wrong | Partly right | Correct |
| **Fix** | Wrong or unsafe | Needs changes | Correct and minimal |
| **Evidence** | None or invented | Partly supports the answer | Clearly supports the answer |

For the false-alarm case, give full marks for file and fix only when the agent blames no file and proposes no code change.

Scoring process:

1. Export the results with random IDs, and hide the condition and run number.
2. Score all 54 runs using the rubric and the answers written in advance.
3. Test proposed fixes in an isolated environment. Use the result to confirm the fix score.
4. Reveal the conditions only after scoring is complete.
5. Save the scores and short notes in LangSmith or a results file.

Optional: ask another developer to score a sample independently, then report any differences.

## 7. Measurements and reporting

### Primary measures

- **Correct root cause count:** runs that score 2 for both file and root cause
- **False-alarm handling:** runs that correctly report no code bug in B6

### Secondary measures

- Rubric score by criterion
- Number of fixes that pass their verification check
- Total tokens and estimated cost per run
- Latency per run
- Tool calls per run
- Invalid output count
- Failure type: wrong file, wrong cause, invalid fix, invented bug or insufficient context

### Reporting

- Present counts for each condition and case, such as "5 of 6".
- Show the variation across the three runs for each case.
- Review failed traces and explain why each failure happened.
- Treat the results as a case study, without percentages, significance tests or confidence intervals.
- State the limitations: one simple app, hand-created cases and one primary scorer.

## 8. Product requirements

### Functional requirements

| ID | Priority | Requirement |
|---|---|---|
| FR1 | Must | The React demo app captures render, event-handler and unhandled promise errors. |
| FR2 | Must | Each captured log includes the error message, stack trace if available, component stack if available, path, time and commit SHA. |
| FR3 | Must | The API stores captured logs in JSONL format for test case creation. |
| FR4 | Must | The agent can list and read allowed source files from one configured GitHub repository. |
| FR5 | Must | Repository tools read only the deployed commit that produced the problem. |
| FR6 | Must | The API returns structured output: whether a code bug was found, file path, root cause, explanation, proposed fix, confidence and evidence. |
| FR7 | Must | An experiment runner executes all conditions from the frozen test cases. |
| FR8 | Must | LangSmith stores traces for every run, linked to the case and condition. |
| FR9 | Must | Proposed fixes are tested in an isolated temporary copy of the repository. |
| FR10 | Must | A script creates a blinded scoring sheet and joins the scores back to the results afterward. |
| FR11 | Should | The React page shows the diagnosis and evidence for a selected log. |
| FR12 | Could | The analysis script exports charts and a results table. |

### API

```http
POST /api/logs
POST /api/debug
GET  /health
```

Example `POST /api/debug` request:

```json
{
  "input": "TypeError: Cannot read properties of undefined...",
  "commit_sha": "abc1234"
}
```

Example response:

```json
{
  "code_bug_found": true,
  "file_path": "src/components/Profile.jsx",
  "root_cause": "The component assumes user.profile always exists.",
  "explanation": "The stack trace points to the render path that reads profile.name.",
  "proposed_fix": "Return a fallback when profile is missing.",
  "confidence": 0.84,
  "evidence": ["Profile.jsx reads user.profile.name without a check"]
}
```

## 9. Architecture

```text
React demo app ──> POST /api/logs ──> JSONL logs ──> Frozen test cases
       │                                                  │
       └──────────> POST /api/debug                       v
                         │                         Experiment runner
                         v                                │
                    Agent loop <──────────────────────────┘
                     │        │
          GitHub read tools   LangSmith traces
                     │
                     v
              Structured diagnosis ──> Blinded human scoring
                     │
                     └───────────────> Isolated fix check
```

### Agent loop

One graph serves every condition. The model, system prompt and diagnosis schema stay the same. The condition decides whether any file is preloaded and whether repository tools are available.

```text
START
  |
  v
prepare
  |  C1: error log. Tools off.
  |  C2: error log + the stack-trace file at commit_sha. Tools off.
  |  C3: error log. Tools on.
  v
+--> model -- C1, C2, or no tool call --> diagnosis --> END
|      |
|      +-- C3 tool call, and tool_calls_used < 8 --> tools
|                                                      |
+------------------------------------------------------+
                    list_files(path)
                    read_file(path)
                    both at commit_sha

After the 8th tool result, the return edge visits model with tools turned off.
That visit can only go to diagnosis.
```

| From | To | When |
|---|---|---|
| prepare | model | Always. C2 has already loaded the one implicated file. C3 has loaded nothing else. |
| model | tools | C3 only. The model called `list_files` or `read_file`, and fewer than 8 tool calls have run. |
| tools | model | The tool result is appended. A blocked path or tool error is still a result, and it still counts. The 8th result returns with tools turned off. |
| model | diagnosis | C1, C2, or this visit requested no tool. That response is the diagnosis. |
| diagnosis | END | The diagnosis matches the `POST /api/debug` schema. An invalid diagnosis is stored and counted. It is not sent around the loop again. |

Each visit to `model` sees the error log, the C2 file when this is a C2 run, and the tool results so far. It does not see the rest of the repository.

`tools` accepts two calls, both fixed to `commit_sha`. Define each tool in its own file under `backend/agent/tools/`:

- `backend/agent/tools/list_files.py` lists allowed source files under a path.
- `backend/agent/tools/read_file.py` returns one allowed source file.

Both reject `.env`, secrets, deployment files and any path outside the allowlist. The rejection text is the observation the model reads next.

C3 is this loop: the model chooses a file, reads the observation, and chooses again, until it can fill the diagnosis or it has used 8 tool calls. C1 and C2 are the same graph with the tool edge removed, so they remain the non-agent baselines.

### Diagnosis schema

The `diagnosis` step uses one Pydantic model for every condition, defined in `backend/agent/schemas/diagnosis.py`. LangChain accepts that model as `response_format`, so the model returns the `POST /api/debug` fields directly: `code_bug_found`, `file_path`, `root_cause`, `explanation`, `proposed_fix`, `confidence`, and `evidence`.

C1 and C2 use this model on their single model call. C3 uses it when the loop stops. If validation fails, store that run and count it as an invalid diagnosis. The graph does not send it back through the loop.

Pydantic checks this last response only. `list_files` and `read_file` stay ordinary tools.

### Web search

Tavily stays out of `prepare`, `model`, and `tools` for the 54 scored runs. The study measures how much of the deployed repository the model can see. A search result is another context: the model could answer from a React article instead of the commit that produced the log, and the call would count toward the 8-tool cap and the token, cost, and latency measures.

Tavily may be used while preparing the six cases. It may also be added as its own condition after those 54 runs are frozen and scored. A search query includes the error log, so it goes to Tavily only during that preparation or later condition.

### AWS demo

- **React app:** S3 and CloudFront
- **API:** Docker on ECS Fargate behind an Application Load Balancer
- **Secrets:** AWS Secrets Manager
- **Logs:** CloudWatch

The experiment and fix checks can run locally. AWS hosts the demo, not the evaluation workload.

### Suggested repository structure

```text
react-debug-agent-lab/
├── README.md
├── prd.md
├── frontend/
├── backend/
│   ├── app/
│   ├── agent/
│   │   ├── tools/
│   │   │   ├── list_files.py
│   │   │   └── read_file.py
│   │   └── schemas/
│   │       └── diagnosis.py
│   └── tests/
├── evals/
│   ├── cases/
│   ├── conditions/
│   ├── scoring/
│   └── run_experiment.py
├── analysis/
├── results/
└── infra/
```

## 10. Security and ethics

- Use only demo code and synthetic data.
- Give the GitHub token read-only access to the one demo repository.
- Limit tools to allowed source file paths and block `.env`, secrets and deployment files.
- Treat logs and source code as untrusted data, because they may contain prompt injection text.
- Remove secrets and personal data before sending logs to the LLM or LangSmith.
- During the 54 scored runs, send logs and source only to the model provider, LangSmith, and the demo repository.
- Never run proposed code on the API server.
- Run tests in a short-lived container with no secrets, cloud credentials or network access, and with CPU, memory and time limits.
- Keep the intentionally vulnerable code in the demo copy, and never deploy it publicly.
- Protect the deployed API with authentication and rate limits.
- Set AWS and LLM budget limits.
- Disclose that the bugs were intentionally created and that AI helped produce any evaluated output.

## 11. Limitations

| Limitation | Mitigation |
|---|---|
| Six cases can't support general conclusions | Describe the study as exploratory and report counts |
| One simple app may be easier than real projects | State this clearly and don't generalize to larger repositories |
| The author creates and scores the cases | Write answers in advance and score without seeing the condition |
| Only one case is designed around a cause outside the stack trace file | Treat RQ2 findings as an initial signal |
| LLM output varies | Repeat each case 3 times and show the variation |
| A fix can pass a test and still be poor | Score fix quality separately and review each fix |

## 12. One-week plan

| Day | Deliverable |
|---|---|
| **1** | Repository, demo app, logging and API skeleton |
| **2** | GitHub tools, commit pinning and structured agent output |
| **3** | Six test cases, written answers, verification checks and scoring rubric |
| **4** | Experiment runner, LangSmith tracing, blinded scoring sheet and setup test |
| **5** | Main run of all 54 experiments |
| **6** | Human scoring, fix checks, failure analysis and AWS demo deployment |
| **7** | README, written report, demo video and final cleanup |

**If time runs short:** reduce the runs to 2 per condition, for 36 in total. Remove the deployed frontend before removing the evaluation.

## 13. Deliverables

- Public GitHub repository, if the demo code is safe to publish
- Six test cases, written answers and verification checks
- Reproducible experiment commands
- LangSmith traces and experiment summary
- Scoring rubric, blinded scores and failure analysis
- Results table
- Deployed AWS demo
- Short report or Medium article
- 3-minute demo video

## 14. Acceptance criteria

The project is complete when:

- [ ] All six cases reproduce their recorded problems.
- [ ] Each case with a code bug passes its verification check using the reference fix.
- [ ] Answers and the rubric are saved before the main run.
- [ ] All 54 runs complete, or every failed run is reported.
- [ ] Every run has a LangSmith trace linked to its case and condition.
- [ ] Repository tools are verified to read only the deployed commit and allowed files.
- [ ] All completed runs are scored without showing the condition.
- [ ] Results include the measures in Section 7 and the limitations in Section 11.
- [ ] The AWS demo returns a diagnosis for a sample error.
- [ ] Another developer can reproduce the experiment using the README and their own API keys.

## 15. Risks

| Risk | Response |
|---|---|
| A case can't be reproduced reliably | Replace it with another case of the same type before freezing the test cases |
| Human scoring takes too long | Reduce the runs to 2 per condition before the main run |
| LLM costs exceed the budget | Test the setup first and set a spending limit |
| GitHub API limits slow the runs | Cache files by commit and path |
| Test environment is unreliable | Use one locked Docker image and fixed dependency versions |
| AWS setup delays the project | Deploy with Docker on one EC2 instance |

## 16. Long-term plan

Switch this repository to a private repository, and use it in production for multiple React and GraphQL projects.
