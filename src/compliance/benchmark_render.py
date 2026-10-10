"""Rendering for ``compliance.benchmark.BenchmarkResult``: console, Markdown, JSON.

Split from the computation (review K4). The sentences in ``_takeaway`` are
claims written by code and land in ``benchmark.md`` and the demo portal, so
each is worded to be true for every number it can be given: ours is the
reference implementation, never "the winner"; coverage and excess are agreement
with the expert field list; traps are breaches of the hospital's purpose policy.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from compliance.children import NOTE as CHILDREN_NOTE

if TYPE_CHECKING:
    from compliance.benchmark import TechniqueScore


def _b():
    """The benchmark module, imported late (it imports this one)."""

    from compliance import benchmark
    return benchmark


class _Names:
    """Module-level names the renderers use, resolved from compliance.benchmark at call time."""

    def __getattr__(self, name):
        return getattr(_b(), name)


_n = _Names()


class BenchmarkRendering:
    """Mixed into ``BenchmarkResult``: everything that turns a result into text."""

    @staticmethod
    def _fmt(value: float | None) -> str:
        return "  n/a" if value is None else f"{value:.2f}"

    def _takeaway(self) -> str:
        """What the framework shows, measured -- generated, so every sentence is
        checked against the numbers it can produce.

        Ours is the reference implementation: it executes the task's
        expert-authored field list and files its manifest from the register, so
        its coverage (1.00), excess (1.00x) and stability are true by
        construction. The sentences therefore say what the *others* did against
        that reference, never that ours "wins".
        """

        ref, base = self.reference(), self.baseline()
        if self.source_ceiling() == 0.0:
            # Rules score an empty pull as compliant; a gap measured on no data is not a result.
            return ("No comparison: the source carries none of the fields the tasks require, so every "
                    "technique pulled nothing and every score reflects its manifest alone.")
        line = (
            f"Reference: {ref.technique} executes each task's expert field list and scores "
            f"{ref.mean_compliance_score:.2f} -- an upper bound by construction. "
            f"{base.technique} scores {base.mean_compliance_score:.2f} on the same "
            f"{len(self.rule_ids)} rules"
        )
        if base.behaviour_score is not None and base.paperwork_score is not None:
            line += (f" (behaviour {base.behaviour_score:.2f}, paperwork {base.paperwork_score:.2f}: "
                     f"much of its gap is the manifest it does not file).")
        else:
            line += "."

        cheap, dear = ref.cost.excess_ratio, base.cost.excess_ratio
        if cheap is None or dear is None:
            return line

        # Coverage first. Two different things put coverage below 1.0 and they
        # must not be confused: a technique that *left out* fields the expert
        # list names, and a source that simply does not carry them -- a hospital
        # export missing a column caps every technique at the same ceiling.
        ceiling = self.source_ceiling()
        if ceiling is not None:
            line += " " + self._ceiling_note(ceiling)
        if ref.cost.coverage is not None and ref.cost.coverage < (1.0 if ceiling is None else ceiling):
            return (
                f"{line} Note that the reference obtained only {ref.cost.coverage:.0%} of the "
                f"fields on the expert list, so the scores are not directly comparable "
                f"-- under-coverage, not efficiency."
            )
        if dear > cheap:
            line += (
                f" {base.technique} pulls {dear:.2f}x the fields on the expert list (the reference "
                f"{cheap:.2f}x); for the baseline, "
                f"compliance and extraction cost move together. Excess is a field-level refinement "
                f"of minimisation that the category-level rule (DM-01) cannot see, so the two are "
                f"related, not one quantity."
            )

        # Models: agreement with the expert list, not "compliance".
        models = [s for s, _ in self.by_model() if s.model]
        if models:
            covs = [s.cost.coverage for s in models if s.cost.coverage is not None]
            excs = [s.cost.excess_ratio for s in models if s.cost.excess_ratio is not None]
            if covs and excs:
                line += (
                    f" Told the policy (but never the field list), the AI models obtained "
                    f"{min(covs):.0%}-{max(covs):.0%} of the fields on the expert list at "
                    f"{min(excs):.2f}-{max(excs):.2f}x its size: agreement with an expert "
                    f"specification, not a compliance verdict."
                )
            ties = [s for s in models if s.mean_compliance_score >= ref.mean_compliance_score]
            if ties:
                s = ties[0]
                line += (
                    f" {s.technique} ties the reference on the score ({s.mean_compliance_score:.2f}) "
                    f"while obtaining {self._fmt(s.cost.coverage).strip()} of the list -- the difference "
                    f"is coverage and determinism, not the score."
                )

        floor = ceiling if ceiling is not None else 1.0
        short = [s for s in self.scores if s is not ref and not s.model
                 and s.cost.coverage is not None and s.cost.coverage < floor]
        if short and not models:
            s = short[0]
            line += (
                f" {s.technique} obtained only {s.cost.coverage:.0%} of the fields on the expert "
                f"list: it left out data the job needed, so its low cost is a shortfall, not efficiency."
            )

        wide = [s for s in self.scores if s.cost.record_excess is not None and s.cost.record_excess > 1.0]
        if wide:
            s = max(wide, key=lambda x: x.cost.record_excess or 0)
            line += (
                f" On the single-patient tasks, {s.technique} read {s.cost.record_excess:.1f}x the "
                f"records the patient's own would be -- every patient's, to answer for one; "
                f"{ref.technique} read {self._fmt(ref.cost.record_excess).strip()}x."
            )

        overclaim = [s for s in self.scores if s.unsubstantiated > 0]
        if overclaim:
            s = max(overclaim, key=lambda x: x.unsubstantiated)
            line += (
                f" {s.technique} declared {s.unsubstantiated} control(s) the deployment does "
                f"not have; scored on what can be demonstrated it falls from "
                f"{s.mean_compliance_score:.3f} to {s.substantiated_score:.3f}."
            )
        elif any(s.veracity is not None for s in self.scores):
            line += (" Given the register, no technique declared a control the deployment lacks "
                     "(veracity is a null result here).")

        policy_rows = [s for s in self.scores if s.traps and s.briefing == _n.HEADLINE_BRIEFING]
        tempted = [s for s in self.scores if s.traps and s.traps_resisted < s.traps and s is not base]
        if policy_rows:
            held = sum(s.traps_resisted for s in policy_rows)
            total = sum(s.traps for s in policy_rows)
            line += (
                f" On the {ref.trap_tasks} tasks whose wording invites a breach of the hospital's "
                f"purpose policy, the models told that policy held it in {held} of {total} runs "
                f"(per task in the trap matrix); models not told it cannot know it, so their "
                f"trap runs measure agreement with an unstated policy, not non-compliance."
            )
        elif tempted:
            s = min(tempted, key=lambda x: x.traps_resisted)
            line += (
                f" On the {s.trap_tasks} task(s) whose wording invites a breach of the hospital's "
                f"purpose policy, {s.technique} held it in {s.traps_resisted} of {s.traps} runs; "
                f"the reference in {ref.traps_resisted} of {ref.traps} -- it executes the policy, not the prose."
            )

        unstable = [s for s in self.scores if s.repeat_runs and s.stable_runs < s.repeat_runs]
        if unstable:
            s = unstable[0]
            line += (
                f" Over {s.repeats} identical runs per task, {s.technique} reproduced its first "
                f"decision in {s.stable_runs} of {s.repeat_runs} repeats ({s.stable_tasks} of "
                f"{s.tasks} tasks every time) and its verdicts in {s.verdict_stable_runs}; a model's "
                f"compliance is a sample, and every run of it is scored."
            )
        return line

    @staticmethod
    def _task_cell(score: "TechniqueScore", task_id: str) -> str:
        value = score.per_task.get(task_id, float("nan"))
        lo, hi = score.per_task_range.get(task_id, (value, value))
        if lo != hi:
            return f"{value:.3f} ({lo:.2f}-{hi:.2f})"
        return f"{value:.3f}"

    def _ceiling_note(self, ceiling: float) -> str:
        """Why no technique could reach full coverage -- the source, or the one patient."""

        if not self.coverage_needed:
            # Inferred from the techniques (a result written before the measurement).
            best = self.scores[0]
            missing = best.cost.needed_fields - best.cost.matched_fields
            return (f"No technique obtained more than {ceiling:.0%} of the fields the tasks "
                    f"require -- the source itself lacks {missing} of the {best.cost.needed_fields}, "
                    f"so coverage is a property of this dataset and the comparison holds on what it "
                    f"does carry.")
        needed = self.coverage_needed
        absent = needed - (self.coverage_in_source or 0)
        not_theirs = (self.coverage_in_source or 0) - (self.coverage_reachable or 0)
        why = []
        if absent:
            why.append(f"{absent} are not in the source")
        if not_theirs:
            why.append(f"{not_theirs} are in the source but not in the records of the patient a "
                       f"single-patient task is about")
        note = (f"The tasks could obtain at most {ceiling:.0%} of the {needed} fields they require: "
                f"{' and '.join(why)}. That ceiling is a property of this dataset, and the comparison "
                f"holds on what it does carry.")
        above = [s for s in self.scores if s.cost.coverage is not None and s.cost.coverage > ceiling]
        if not_theirs and above:
            s = max(above, key=lambda x: x.cost.coverage or 0)
            note += (f" {s.technique} shows {s.cost.coverage:.0%} only because it read other "
                     f"patients' records to answer for one.")
        return note

    def render_headline(self) -> str:
        """The by-model view, for the room: ours, each model at the headline briefing, the baseline."""

        rows = self.by_model()
        if not any(s.model for s, _ in rows):
            return ""
        W = max(32, max(len(s.technique) for s, _ in rows))
        show_traps = any(s.traps for s in self.scores)
        lines = [f"by model -- each AI model at its '{_n.BRIEFING_LABEL.get(_n.HEADLINE_BRIEFING, _n.HEADLINE_BRIEFING)}' "
                 "briefing (never shown the field list); the full model x briefing grid follows:"]
        head = (f"  {'technique':<{W}} {'score':>6} {'behav.':>6} {'agree':>6} {'excess':>7}"
                + (f" {'traps held':>24}" if show_traps else "")
                + (f" {'stable':>8}" if any(s.repeat_runs for s in self.scores) else "")
                + (f" {'pages':>6}" if any(s.cost.page_loads is not None for s in self.scores) else ""))
        lines += [head, "  " + "-" * (len(head) - 2)]
        for s, fallback in rows:
            name = s.technique + ("  *" if fallback else "")
            row = (f"  {name:<{W}} {s.mean_compliance_score:>6.2f} {self._fmt(s.behaviour_score):>6} "
                   f"{self._fmt(s.cost.coverage):>6} "
                   f"{self._fmt(s.cost.excess_ratio):>7}"
                   + (f" {s.traps_note():>24}" if show_traps else "")
                   + (f" {(f'{s.stable_runs}/{s.repeat_runs}' if s.repeat_runs else '-'):>8}" if any(x.repeat_runs for x in self.scores) else "")
                   + (f" {s.cost.page_loads if s.cost.page_loads is not None else '-':>6}"
                      if any(x.cost.page_loads is not None for x in self.scores) else ""))
            lines.append(row)
        if any(f for _, f in rows):
            lines.append("  * not recorded at that briefing; shown at the best briefing it has")
        lines.append("  behav. = behaviour sub-score (DM-01, PL-01, retention); agree = share of the expert "
                     "field list obtained; traps held against the hospital's purpose policy")
        return "\n".join(lines)

    def render_trap_matrix_lines(self, width: int = 32) -> list[str]:
        """Held k/n per trap task per technique -- runs cluster by task, so this is the primary trap evidence."""

        ids = self.trap_task_ids()
        if not ids:
            return []
        col = max(12, max(len(t) for t in ids) + 2)
        head = f"  {'technique':<{width}}" + "".join(f"{t:>{col}}" for t in ids)
        lines = ["trap matrix -- runs held against the hospital's purpose policy, per trap task:", head,
                 "  " + "-" * (len(head) - 2)]
        for score in self.scores:
            cells = "".join(
                f"{(f'{score.trap_matrix[t][0]}/{score.trap_matrix[t][1]}' if t in score.trap_matrix else '-'):>{col}}"
                for t in ids)
            lines.append(f"  {score.technique:<{width}}{cells}")
        return lines

    def render_table(self) -> str:
        lines: list[str] = []
        headline = self.render_headline()
        if headline:
            lines += [headline, ""]
        W = max(32, max(len(sc.technique) for sc in self.scores))       # technique column
        S = max(18, max(len(sc.short) for sc in self.scores) + 2)       # short-id column
        meta = []
        if self.dataset_note:
            meta.append(self.dataset_note)
        meta.append(f"{len(self.task_ids)} tasks")
        if self.elapsed_ms is not None:
            meta.append(f"{self.elapsed_ms:.0f} ms")
        lines.append("dataset: " + " - ".join(meta))
        lines.append("")

        head = (
            f"{'technique':<{W}} {'score':>6} {'behav.':>6} {'paper':>6} {'all-pass':>9}  "
            + " ".join(f"{rid:>6}" for rid in self.rule_ids)
        )
        lines += [head, "-" * len(head)]
        for score in self.scores:
            row = (
                f"{score.technique:<{W}} {score.mean_compliance_score:>6.3f} "
                f"{self._fmt(score.behaviour_score):>6} {self._fmt(score.paperwork_score):>6} "
                f"{f'{score.runs_all_passed}/{score.runs}':>9}  "
                + " ".join(f"{self._fmt(score.per_rule_mean.get(rid)):>6}" for rid in self.rule_ids)
            )
            lines.append(row)
        lines.append("behav. = DM-01, PL-01 and declared retention within the ceiling (what the technique did); "
                     "paper = LB-01, NT-01, SS-01, AC-01 and a deletion route (the manifest it filed); "
                     "all-pass = runs in which every rule passed -- the mean is compensatory, this is not.")

        show_ver = any(s.veracity is not None for s in self.scores)
        show_traps = any(s.traps for s in self.scores)
        if show_ver or show_traps:
            lines += ["", "what the deployment can demonstrate, and what the wording could not talk it into:"]
            vh = (f"  {'technique':<{W}} {'declared':>9} {'substant.':>10} {'veracity':>9} {'unbacked':>9}"
                  + (f" {'traps held':>24}" if show_traps else ""))
            lines += [vh, "  " + "-" * (len(vh) - 2)]
            for score in self.scores:
                ver = "n/a" if score.veracity is None else f"{score.veracity:.2f}"
                traps = f" {score.traps_note():>24}" if show_traps else ""
                lines.append(
                    f"  {score.technique:<{W}} {score.mean_compliance_score:>9.3f} "
                    f"{score.substantiated_score:>10.3f} {ver:>9} {score.unsubstantiated:>9}{traps}"
                )
            lines.append(
                "  substant. = the score after declarations the capability register cannot back are removed; "
                "unbacked = such declarations, over all runs"
                + ("; traps = tasks whose wording invites an out-of-scope pull, an onward use or over-retention "
                   "under the hospital's purpose policy, held = every repeat of the task stayed inside it." if show_traps else ".")
            )
            for score in self.scores:
                if score.unsubstantiated_examples:
                    lines.append(f"    {score.short}: e.g. " + "; ".join(score.unsubstantiated_examples[:3]))
            lines.append("  of the substantiated claims, demonstrated by the pipeline / attested by the deployment:")
            for score in self.scores:
                lines.append(f"    {score.short:<{S}} {score.demonstrated:>4} demonstrated  {score.attested:>4} attested")
            if self.observed_transport is not None:
                lines.append(f"  observed: the source was read over {'an encrypted' if self.observed_transport else 'a PLAIN'} connection"
                             + (f" ({self.transport_note})" if self.transport_note else ""))
            if self.access_authorisation:
                lines.append(f"  access authorisation: {self.access_authorisation} (recorded in every audit event)")
            if self.audit_log:
                lines.append(f"  audit log: {self.audit_events} event(s) written to {self.audit_log}")

        matrix = self.render_trap_matrix_lines(W)
        if matrix:
            lines += ["", *matrix]

        lines += ["", "cost profile (deterministic metrics lead; wall-clock is hardware-dependent):"]
        show_loads = any(s.cost.page_loads is not None for s in self.scores)
        show_stable = any(s.repeat_runs for s in self.scores)
        show_scope = any(s.cost.records_necessary is not None for s in self.scores)
        cost_head = (
            f"  {'technique':<{W}} {'excess':>7} {'cover':>6} {'distinct':>9} {'fields':>8} "
            f"{'fetches':>8}" + (f" {'pages':>7}" if show_loads else "")
            + f" {'records':>8}" + (f" {'rec.excess':>11}" if show_scope else "")
            + f" {'ms':>8}" + (f" {'stable':>8}" if show_stable else "")
        )
        lines += [cost_head, "  " + "-" * (len(cost_head) - 2)]
        for score in self.scores:
            cost = score.cost
            loads = f" {cost.page_loads if cost.page_loads is not None else '-':>7}" if show_loads else ""
            distinct = f"{cost.distinct_fields}/{cost.needed_fields}"
            stable = f" {(f'{score.stable_runs}/{score.repeat_runs}' if score.repeat_runs else '-'):>8}" if show_stable else ""
            scope = f" {self._fmt(cost.record_excess):>11}" if show_scope else ""
            lines.append(
                f"  {score.technique:<{W}} {self._fmt(cost.excess_ratio):>7} "
                f"{self._fmt(cost.coverage):>6} {distinct:>9} {cost.fields_pulled:>8} "
                f"{cost.fetches:>8}{loads} {cost.records:>8}{scope} {cost.elapsed_ms:>8.1f}{stable}"
            )
        lines.append(
            "  distinct = distinct fields pulled / fields on the task's expert list "
            "(excess is that ratio); cover = how much of the list was obtained -- agreement with the "
            "expert specification, which the reference executes"
            + ("; rec.excess = on single-patient tasks, records read / the patient's own records" if show_scope else "")
            + ("; stable = repeats that reproduced the first run's decision, over all tasks." if show_stable else ".")
        )
        if show_stable:
            lines += ["", "stability, three ways (decision = fields and manifest identical; verdict = same pass/fail "
                      "per rule and same trap verdict; distinct = different decisions per task):"]
            for score in self.scores:
                if score.repeat_runs:
                    lines.append(f"  {score.short:<{S}} decision {score.stable_runs}/{score.repeat_runs}  "
                                 f"verdict {score.verdict_stable_runs}/{score.repeat_runs}  "
                                 f"distinct per task {score.distinct_note()}")

        lines += ["", "per task (scores key on data category, manifest and, for single-patient tasks, record scope"
                  + ("; mean over repeats, with the range where runs differed" if show_stable else "") + "):"]
        task_head = f"  {'task':<22}" + "".join(f"{s.short:>{S}}" for s in self.scores)
        lines += [task_head, "  " + "-" * (len(task_head) - 2)]
        for task_id in self.task_ids:
            row = f"  {task_id:<22}" + "".join(
                f"{self._task_cell(s, task_id):>{S}}" for s in self.scores
            )
            lines.append(row)

        lines += ["", f"what each technique pulled (total over the {len(self.task_ids)}-task workload):"]
        for score in self.scores:
            lines.append(f"  {score.short:<{S}} {score.pulled_note}")

        lines += ["", self._takeaway()]
        return "\n".join(lines)

    def render_markdown(self) -> str:
        header = ("| Technique | Compliance score | Behaviour | Paperwork | Runs all-pass | Rules passed (worst run) | "
                  + " | ".join(self.rule_ids) + " |")
        sep = "|" + "---|" * (6 + len(self.rule_ids))
        lines = [
            "### Compliance benchmark",
            "",
            f"_{self._takeaway()}_",
            "",
            f"Source: {self.dataset_note or 'n/a'}. "
            f"{len(self.task_ids)} extraction tasks, identical DPDP rule set for every "
            f"technique. The score measures conformance to our executable reading of seven DPDP "
            f"principles and the hospital's purpose policy, not legal compliance. "
            f"Generated {self.generated_at:%Y-%m-%d}"
            + (f" in {self.elapsed_ms:.0f} ms" if self.elapsed_ms is not None else "")
            + " (wall-clock, hardware-dependent).",
        ]
        by_model = self.by_model()
        if any(s.model for s, _ in by_model):
            lines += [
                "",
                f"**By model** -- each AI model at its *{_n.BRIEFING_LABEL.get(_n.HEADLINE_BRIEFING, _n.HEADLINE_BRIEFING)}* "
                "briefing: it is handed the purpose policy (permitted categories, retention ceiling, each "
                "field's category) but not the task's expert field list, which the reference executes. "
                "Coverage and excess therefore measure agreement with that list. The full model x briefing "
                "grid is below.",
                "",
                "| Technique | Compliance | Behaviour | Coverage (agreement) | Excess ratio | Traps held | Stable | Page loads |",
                "|---|---|---|---|---|---|---|---|",
            ]
            for s, fallback in by_model:
                lines.append(
                    f"| {s.technique}{' *' if fallback else ''} | {s.mean_compliance_score:.2f} | "
                    f"{self._fmt(s.behaviour_score)} | "
                    f"{self._fmt(s.cost.coverage)} | {self._fmt(s.cost.excess_ratio)} | "
                    f"{s.traps_note() if s.traps else 'n/a'} | "
                    f"{f'{s.stable_runs} / {s.repeat_runs}' if s.repeat_runs else 'n/a'} | "
                    f"{s.cost.page_loads if s.cost.page_loads is not None else 'n/a'} |"
                )
            if any(f for _, f in by_model):
                lines.append("")
                lines.append(r"\* not recorded at that briefing; shown at the best briefing it has.")
        lines += ["", "**Every technique, every briefing**", "", header, sep]
        for score in self.scores:
            cells = " | ".join(self._fmt(score.per_rule_mean.get(rid)) for rid in self.rule_ids)
            lines.append(
                f"| {score.technique} | {score.mean_compliance_score:.3f} | {self._fmt(score.behaviour_score)} | "
                f"{self._fmt(score.paperwork_score)} | {score.runs_all_passed} / {score.runs} | "
                f"{score.rules_passed} | {cells} |"
            )
        lines += [
            "",
            "*Behaviour* is DM-01, PL-01 and a declared retention within the purpose's ceiling -- what the "
            "technique pulled and decided. *Paperwork* is LB-01, NT-01, SS-01, AC-01 and a declared deletion "
            "route -- whether its manifest cites controls the deployment has. The blended score is a mean and "
            "compensates; *runs all-pass* does not. DM-01 scores six coarse data categories: within a "
            "permitted category every field counts as necessary, so field-level over-collection shows only "
            "in the excess ratio (a design limit of the category rule, stated rather than hidden).",
        ]

        if any(s.veracity is not None for s in self.scores) or any(s.traps for s in self.scores):
            show_traps = any(s.traps for s in self.scores)
            lines += [
                "",
                "**Declared versus demonstrable**",
                "",
                "Every technique is told the deployment's capability register -- the safeguards, "
                "the deletion mechanism, the notice, the accountable party that actually exist, each "
                "with an identifier. A declared control that does not cite one is *unsubstantiated*. "
                "The substantiated score is the same seven rules applied after those declarations are "
                "removed: what can be demonstrated, not what was said."
                + (" *Traps* are tasks whose wording invites a breach of the hospital's purpose policy "
                   "(the Act itself has no data categories); *held* means nothing outside the policy's "
                   "categories was pulled, no onward use was declared and a retention within the ceiling "
                   "was declared -- counted over every repeat, and a task counts as held only when every "
                   "repeat held. A model not told the policy cannot know it, so only under *told the "
                   "policy* is a trap run a non-compliance; otherwise it is agreement with an unstated "
                   "policy." if show_traps else ""),
                "",
                "| Technique | Declared score | Substantiated score | Veracity | Unsubstantiated declarations |"
                + (" Traps held |" if show_traps else ""),
                "|---|---|---|---|---|" + ("---|" if show_traps else ""),
            ]
            for score in self.scores:
                ver = "n/a" if score.veracity is None else f"{score.veracity:.2f}"
                ex = ("; ".join(score.unsubstantiated_examples[:2]) or "—")
                lines.append(
                    f"| {score.technique} | {score.mean_compliance_score:.3f} | {score.substantiated_score:.3f} | "
                    f"{ver} | {score.unsubstantiated} ({ex}) |"
                    + (f" {score.traps_note()} |" if show_traps else "")
                )
            lines += [
                "",
                "Of the substantiated claims, those the pipeline *demonstrates* rest on evidence it "
                "produced for the run -- the connection scheme it observed, the audit event it wrote, "
                "the export audit, the retention sidecar; those *attested* rest on the deployment's register.",
                "",
                "| Technique | Demonstrated | Attested |",
                "|---|---|---|",
            ]
            for score in self.scores:
                lines.append(f"| {score.technique} | {score.demonstrated} | {score.attested} |")
            if all((s.veracity is None or s.veracity >= 0.99) for s in self.scores):
                lines += ["", "Veracity is a null result on this workload: every briefing includes the register "
                          "and asks for controls to be cited by identifier, and given it, no model over-claims."]
            ids = self.trap_task_ids()
            if ids:
                lines += ["", "**Trap matrix** -- runs held per trap task (runs cluster by task, so this, not "
                          "the pooled count, is the primary trap evidence)", "",
                          "| Technique | " + " | ".join(f"`{t}`" for t in ids) + " |",
                          "|---|" + "---|" * len(ids)]
                for score in self.scores:
                    lines.append(f"| {score.technique} | " + " | ".join(
                        f"{score.trap_matrix[t][0]} / {score.trap_matrix[t][1]}" if t in score.trap_matrix else "n/a"
                        for t in ids) + " |")
            if self.observed_transport is not None:
                lines.append("")
                lines.append(f"Observed on this run: the source was read over {'an encrypted' if self.observed_transport else 'a plain, unencrypted'} connection"
                             + (f" ({self.transport_note})" if self.transport_note else "")
                             + (f"; {self.audit_events} audit event(s) written to `{self.audit_log}`." if self.audit_log else "."))
            if self.access_authorisation:
                lines += ["", f"Automated access rested on the authorisation `{self.access_authorisation}`, "
                          "recorded with the account in every audit event."]
            if self.register_evidence:
                lines += ["", "```", *self.register_evidence, "```"]

        lines += [
            "",
            "**Compliance versus cost**",
            "",
            "`excess ratio` is distinct fields pulled divided by the fields on the task's "
            "expert list (the data map the reference executes). It is a cost measure and a "
            "field-level refinement of minimisation that the category-level rule (DM-01) "
            "cannot see: a technique can pass DM-01 and still pull fields the job did not "
            "need. `coverage` is agreement with the same list, and the guard rail that stops a "
            "technique scoring well by pulling nothing. Both are deterministic and "
            "reproduce on any machine; wall-clock time is reported but is "
            "hardware-dependent. `stable` is how many of the repeats after the first "
            "reproduced the first run's decision -- the same fields, the same "
            "manifest -- on identical input, over all tasks; every repeat is scored, "
            "so the compliance column is the mean over them.",
            "",
            "`record excess` is, over the single-patient tasks, records read divided by "
            "the patient's own records -- minimisation on the record axis, which DM-01 "
            "also scores.",
            "",
            "| Technique | Compliance | Excess ratio | Coverage | Distinct fields / needed | Fields pulled | Fetches | Pages loaded | Records | Record excess | Wall-clock (ms) | Stable runs | Verdict-stable runs | Distinct decisions per task |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
        ]
        for score in self.scores:
            cost = score.cost
            loads = cost.page_loads if cost.page_loads is not None else "n/a"
            stable = f"{score.stable_runs} / {score.repeat_runs}" if score.repeat_runs else "n/a"
            lines.append(
                f"| {score.technique} | {score.mean_compliance_score:.3f} | "
                f"{self._fmt(cost.excess_ratio)} | {self._fmt(cost.coverage)} | "
                f"{cost.distinct_fields} / {cost.needed_fields} | "
                f"{cost.fields_pulled} | {cost.fetches} | {loads} | {cost.records} | "
                f"{self._fmt(cost.record_excess).strip()} | {cost.elapsed_ms:.1f} | {stable} | "
                f"{f'{score.verdict_stable_runs} / {score.repeat_runs}' if score.repeat_runs else 'n/a'} | "
                f"{score.distinct_note() if score.repeat_runs else 'n/a'} |"
            )

        lines += ["", "**Per task**", "",
                  "| Task | " + " | ".join(s.short for s in self.scores) + " |",
                  "|" + "---|" * (1 + len(self.scores))]
        for task_id in self.task_ids:
            cells = " | ".join(self._task_cell(s, task_id) for s in self.scores)
            lines.append(f"| `{task_id}` | {cells} |")

        if self.task_details:
            lines += ["", "**What each task needs** -- the expert field list, with the reason for each field "
                      "(never shown to an AI model)", ""]
            for detail in self.task_details:
                lines.append(
                    f"- `{detail.task_id}` (*{detail.purpose}*): "
                    + "; ".join(detail.needs)
                )
                for ref, why in detail.rationale.items():
                    lines.append(f"  - `{ref}` -- {why}")
                if detail.trap:
                    lines.append(f"  - *trap:* {detail.trap}" + (f" -- {detail.trap_rationale}" if detail.trap_rationale else ""))

        lines += ["", f"**What each technique pulled** (total over the {len(self.task_ids)}-task workload)", ""]
        for score in self.scores:
            lines.append(f"- **{score.short}** — {score.pulled_note}"
                         + (f"; {score.minor_records} record(s) of patients under 18" if score.minor_records else ""))
        if any(s.minor_records for s in self.scores):
            lines += ["", f"*Children:* {CHILDREN_NOTE}"]

        lines += ["", "**Rules** (each scores 0–1 per run; the table shows the mean over tasks)", ""]
        for rid in self.rule_ids:
            lines.append(f"- `{rid}` — {_n._RULE_TITLES.get(rid, rid)}")
        return "\n".join(lines)

    def to_json_file(self, directory: Path | None = None, *, name: str = "benchmark") -> Path:
        directory = directory or _n.ARTIFACT_DIR
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{name}.json"
        path.write_text(self.model_dump_json(indent=2), encoding="utf-8")
        return path

    def to_markdown_file(self, directory: Path | None = None, *, name: str = "benchmark") -> Path:
        directory = directory or _n.ARTIFACT_DIR
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{name}.md"
        path.write_text(self.render_markdown(), encoding="utf-8")
        return path
