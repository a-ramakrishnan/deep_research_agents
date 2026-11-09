const roles = [
  { name: "Coordinator", cases: [1, 2, 3] },
  { name: "Source researcher", cases: [4, 5, 6, 41] },
  { name: "Evidence assessor", cases: [7, 8, 9, 10, 11, 12, 55] },
  { name: "Change analyst", cases: [13, 14, 15, 16, 17, 18, 19, 20] },
  { name: "Domain analyst", cases: [21, 22, 23, 24, 25, 51, 52, 53, 54, 55, 56, 57, 58] },
  { name: "Report writer", cases: [26, 27, 28, 29, 32] },
  { name: "Reviewer", cases: [30, 31, 32] },
];

let handoffs = [
  ["Scheduler", "Coordinator", "Started a scheduled refresh with a frozen report specification."],
  ["Coordinator", "Source researcher", "Assigned the Acme pricing and SSO check."],
  ["Source researcher", "Evidence assessor", "Captured pricing snapshot S02. S01 is the previous baseline."],
  ["Evidence assessor", "Change analyst", "Validated the Business plan excerpt in S02."],
  ["Change analyst", "Domain analyst", "Detected SSO moving from Enterprise-only to Business using S01 and S02."],
  ["Domain analyst", "Report writer", "Sent revised positioning and accepted findings after the knowledge commit."],
  ["Report writer", "Reviewer", "Submitted the dated draft with both evidence references."],
  ["Reviewer", "Publisher", "Approved the draft for deterministic publication."],
  ["Publisher", "Edition history", "Published the dated edition and retained the previous report."],
];

const byId = (id) => document.getElementById(id);
const slider = byId("step");
const replay = byId("replay");
const filter = byId("filter");
let timer;

function element(tag, text, className) {
  const node = document.createElement(tag);
  node.textContent = text;
  if (className) node.className = className;
  return node;
}

function render() {
  const count = Number(slider.value);
  const visible = handoffs.slice(0, count);
  const active = visible.at(-1)?.[1];
  byId("step-label").textContent = count === handoffs.length
    ? `Edition published · ${count} of ${handoffs.length} events`
    : `${count} of ${handoffs.length} events`;
  byId("agents").replaceChildren(...roles.map(({ name }) => {
    const working = name === active;
    const complete = visible.some(([from]) => from === name);
    const row = element("li", "");
    row.append(element("span", name), element("span",
      working ? "Working" : complete ? "Complete" : "Queued",
      working ? "status working" : complete ? "status complete" : "status"));
    return row;
  }));
  byId("timeline").replaceChildren(...visible.map(([from, to, detail, timestamp], index) => {
    const row = element("li", "");
    row.append(element("small", timestamp ?? `17:00:${String(index * 4).padStart(2, "0")} IST`),
      element("div", `${from} → ${to}`), element("p", detail));
    return row;
  }));
  if (!count) byId("timeline").append(element("li", "Start replay or move the progress slider."));
}

function pause() {
  clearInterval(timer);
  timer = undefined;
  replay.textContent = Number(slider.value) === handoffs.length ? "Replay" : "Play";
}

slider.max = handoffs.length;
slider.addEventListener("input", () => { pause(); render(); });
replay.addEventListener("click", () => {
  if (timer !== undefined) return pause();
  if (Number(slider.value) === handoffs.length) slider.value = 0;
  render();
  replay.textContent = "Pause";
  timer = setInterval(() => {
    slider.value = Number(slider.value) + 1;
    render();
    if (Number(slider.value) === handoffs.length) pause();
  }, 900);
});
render();

for (const [index, role] of roles.entries()) {
  const option = element("option", role.name);
  option.value = index;
  filter.append(option);
}
const activity = await fetch("../relay-output/activity.json", { cache: "no-store" })
  .then((response) => response.ok ? response.json() : null)
  .catch(() => null);
const results = new Map((activity?.evaluations ?? []).map((item) => [item.case_id, item.status]));
if (activity?.runs.length) {
  byId("mode").textContent = "Recorded offline run";
  const picker = byId("edition");
  const report = byId("report");
  for (const [index, run] of activity.runs.entries()) {
    const option = element("option", run.edition.date);
    option.value = index;
    picker.append(option);
  }
  function selectEdition() {
    const run = activity.runs[Number(picker.value)];
    handoffs = run.events.map(({ sender, recipient, detail, timestamp }) =>
      [sender, recipient, detail, timestamp]);
    slider.max = handoffs.length;
    slider.value = handoffs.length;
    report.href = "../relay-output/" + encodeURIComponent(run.report);
    pause();
    render();
  }
  picker.value = activity.runs.length - 1;
  picker.addEventListener("change", selectEdition);
  byId("edition-control").hidden = false;
  report.hidden = false;
  selectEdition();
}

try {
  const response = await fetch("../evals/catalog.json");
  if (!response.ok) throw new Error("Catalog request failed");
  const { cases } = await response.json();
  function renderCases() {
    const selected = filter.value === "" ? cases : cases.filter(
      ({ id }) => roles[Number(filter.value)].cases.includes(Number(id.slice(1))));
    byId("eval-summary").textContent = `${selected.length} of ${cases.length} catalog cases · ${selected.filter(({ id }) => results.get(id) === "passed").length} passed`;
    byId("cases").replaceChildren(...selected.map(({ id, stimulus, critical }) => {
      const row = element("li", "");
      const status = { passed: "Passed", failed: "Failed", error: "Error" }[results.get(id)] ?? "Not run";
      row.append(element("span", `${id} · ${stimulus}`),
        element("span", critical ? `Critical · ${status}` : status, "status"));
      return row;
    }));
  }
  filter.addEventListener("change", renderCases);
  renderCases();
} catch {
  byId("eval-summary").textContent = "Catalog unavailable. Serve the repository root over HTTP.";
}
