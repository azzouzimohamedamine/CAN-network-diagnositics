# 00 - Overview, Implementation Roadmap and Learning Roadmap

## Implementation phases (each ends with tests, doc update and a commit)
| Phase | Content | Commit examples | State |
|---|---|---|---|
| 0-1 | Spec, requirements, architecture, matrix, DBC, E2E, powertrain TX, test matrix | feat: define vehicle CAN architecture / add initial CAN database | **done** |
| 2 | BRAKE/BMS/CLUSTER CAPL, RX supervision, timeouts, debounce, vehicle model, CANoe config guide run | feat: implement brake ECU simulation; feat: add BMS ECU simulation | planned |
| 3 | GATEWAY_ECU routing, latency, filtering | feat: implement gateway routing; test: add gateway validation tests | planned |
| 4 | Diagnostics (tester + ECU side), DTC store, fault injector | feat: add CAPL diagnostics; feat: add fault injection | planned |
| 5 | Python analysis: parse logs, frequency, missing messages, E2E, plots, report | feat: add Python CAN analysis | planned |
| 6 | Regression suite, golden log, DBC compatibility test, final results/figures | docs: add test report | planned |

Rule: later phases never rewrite earlier interfaces; before editing a file its current content is inspected and the reason for the change is recorded in the commit message.

## Learning roadmap (learn -> implement -> test -> document)
| Skill | Learn just enough for | Project task |
|---|---|---|
| CAN fundamentals, DBC | arbitration, signal encoding | Phase 1 (done): matrix + DBC |
| Python, Git/GitHub | cantools, pytest, commits | Phase 1 and 5 |
| CAPL, CANoe | timers, `on message`, `output()`, panels | Phase 2-3 |
| CANalyzer | trace/statistics/filters/replay | Phase 2-5 analysis scenarios |
| ECU architecture, fault handling | debounce, supervision, DTC | Phase 2-4 |
| UDS / OBD-II concepts | sessions, DTC, NRC | Phase 4 |
| Test automation, fault injection | CAPL test modules, regression | Phase 4-6 |
| Requirements, V-Model, ISO 26262 concepts | traceability, safety goals | prepares Project 6 |
| C/C++, STM32 | layered drivers | Project 2 |
| AUTOSAR concepts | Application/RTE/BSW | Projects 2, 4 |
| MATLAB/Simulink, Model-Based Design | vehicle/sensor models | Project 3, 5 |
Do not study ahead: take only what the next phase needs.

## Official references (concepts only; no documentation copied)
Vector CANoe <https://www.vector.com/fr/product/canoe/>, CANalyzer <https://www.vector.com/fr/product/canalyzer/>, AUTOSAR <https://www.autosar.org/>,
MathWorks Model-Based Design <https://www.mathworks.com/help/simulink/gs/model-based-design.html>, ISO 26262 <https://www.iso.org/standard/90020.html>.
Standards (ISO 11898, ISO 14229, ISO 15765, SAE J1979/J2012) are paid documents: consult your own licensed/university copy.
