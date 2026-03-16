# Linear Docs/Process Migration Table v1

Status: superseded first-pass classification table

Source of truth:
- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/protocol/configs/linear-temporal-layout-spec-v1.md`

Scope:
- `/Users/cjarguello/BitPod-App/bitpod-tools/linear/docs/process/`

Notes:
- Superseded by `linear-docs-process-migration-table-v3.md`. Keep this file only as historical staging context.
- This is a migration table only. No files have been moved by this table.
- Project-specific temporal destinations are not resolved yet because project IDs still need to be attached where applicable.
- First-pass canonical classifications default to `temporal/active/tickets` when project linkage is not yet explicit.

| Current path | Target classification | File type | Reason |
|---|---|---|---|
| `.gitkeep` | `discard-review` | residue | Placeholder file should not survive once the new directory layout exists. |
| `agent_handoff_templates_v1.md` | `protocol/templates` | canonical | Reusable template belongs in canonical protocol templates. |
| `agent_repo_access_parity_2026-03-07.md` | `protocol/agent-references` | canonical | Stable contract or agent-reference material belongs in canonical protocol references. |
| `agent-runtime-portability-plan-v1.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `ai_team_topology_raci_v1.md` | `protocol/agent-references` | canonical | Stable contract or agent-reference material belongs in canonical protocol references. |
| `autopilot_remaining_blockers_dashboard_2026-03-08.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `backup_chatgpt_prompts_preservation_evidence_2026-03-08.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `backup_cleanup_execution_plan_2026-03-07.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `backup_cold_archive_evidence_2026-03-07.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `backup_dedupe_mapping_docs_tools_2026-03-07.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `backup_docs_process_preservation_evidence_2026-03-07.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `backup_final_predelete_checklist_2026-03-07.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `backup_learnings_migration_evidence_2026-03-07.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `backup_reference_candidates_migration_evidence_2026-03-07.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `backup_retirement_classification_matrix_2026-03-07.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `backup_tools_residual_preservation_evidence_2026-03-08.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `backup_uniqueness_scan_2026-03-07.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `backup_workspace_parity_snapshot_2026-03-07.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `bootstrap_closure_gates_matrix_v1.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `bootstrap_phase_normalization_plan_v1.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `bridge_command_surface_cleanup_spec_v1.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `capability_state_truth_label_incident_protocol_v1.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `checkpoints/active_checkpoint_bit127_workspace_rebuild_2026-03-16.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `checkpoints/active_checkpoint_bootstrap_closure_gates_2026-03-12.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `checkpoints/active_checkpoint_phase4_discord_acceptance_2026-03-12.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `checkpoints/active_checkpoint_phase4_engineering_lane_2026-03-12.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `checkpoints/active_checkpoint_phase4_minimum_team_2026-03-12.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `checkpoints/active_checkpoint_phase4_minimum_team_ready_2026-03-12.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `checkpoints/active_checkpoint_phase4_operating_model_2026-03-11.md` | `temporal/active/ticket__BIT-83` | historical | Dated evidence, checkpoint, backup, or status material is non-canonical and belongs in temporal storage. |
| `checkpoints/active_checkpoint_phase4_return_post_taylor01_2026-03-12.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `checkpoints/active_checkpoint_phase4_taylor_discord_general_2026-03-12.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `checkpoints/active_checkpoint_sector_feeds_bit77_2026-03-11.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `checkpoints/active_checkpoint_taylor01_strategy_2026-03-12.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `checkpoints/checkpoint_protocol_adoption_note_2026-03-11.md` | `temporal/active/ticket__BIT-88` | historical | Dated evidence, checkpoint, backup, or status material is non-canonical and belongs in temporal storage. |
| `checkpoints/strict_cleanup_audit_pass_2026-03-15.md` | `temporal/active/tickets` | transitional | This appears operational but not clearly durable canon, so it should be reviewed in temporal storage first. |
| `checkpoints/thread_checkpoint_template_v1.md` | `protocol/templates` | canonical | Reusable template belongs in canonical protocol templates. |
| `ci_pr_smoke_post_transfer_2026-03-07.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `cloudflare_token_scope_upgrade_checklist_2026-03-07.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `communication_surface_portability_v1.md` | `temporal/active/tickets` | transitional | This appears operational but not clearly durable canon, so it should be reviewed in temporal storage first. |
| `delegated_execution_sample_run_v1.md` | `temporal/active/tickets` | transitional | This appears operational but not clearly durable canon, so it should be reviewed in temporal storage first. |
| `discord_command_parity_matrix_v1.md` | `temporal/active/tickets` | transitional | This appears operational but not clearly durable canon, so it should be reviewed in temporal storage first. |
| `discord_migration_architecture_v1.md` | `temporal/active/tickets` | transitional | This appears operational but not clearly durable canon, so it should be reviewed in temporal storage first. |
| `discord_phase2_cj_ui_quickstart_v1.md` | `temporal/active/tickets` | transitional | This appears operational but not clearly durable canon, so it should be reviewed in temporal storage first. |
| `discord_phase2_prereq_execution_runbook_v1.md` | `temporal/active/ticket__BIT-59` | temporal | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `discord_real_acceptance_checklist_v1.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `discord_real_acceptance_status_2026-03-12.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `discord_webhook_parity_checks_v1.md` | `temporal/active/tickets` | transitional | This appears operational but not clearly durable canon, so it should be reviewed in temporal storage first. |
| `dkim_public_selector_scan_2026-03-08.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `domain_email_policy_bitpod_app_v1_2026-03-07.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `durable_artifact_memory_flow_proof_v1.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `email_auth_dns_probe_2026-03-07.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `email_auth_hardening_runbook_2026-03-07.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `email_sender_inventory_sheet_2026-03-07.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `engineering_specialist_lane_contract_v1.md` | `protocol/agent-references` | canonical | Stable contract or agent-reference material belongs in canonical protocol references. |
| `engineering_specialist_lane_operational_proof_v1.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `eval_regression_gate_framework_v1.md` | `temporal/active/tickets` | transitional | This appears operational but not clearly durable canon, so it should be reviewed in temporal storage first. |
| `github_org_baseline_evidence_2026-03-06.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `github_org_baseline_evidence_2026-03-09.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `github_org_baseline_policy_v1.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `github_org_team_access_map_2026-03-07.md` | `temporal/active/tickets` | transitional | This appears operational but not clearly durable canon, so it should be reviewed in temporal storage first. |
| `github_repo_security_matrix_2026-03-07.md` | `temporal/active/tickets` | transitional | This appears operational but not clearly durable canon, so it should be reviewed in temporal storage first. |
| `github-team-purpose-reviewer-routing-v1.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `global-artifact-naming-policy-v1.md` | `bitpod-docs/process` | canonical | Durable workspace-wide naming policy belongs in `bitpod-docs/process`, not under Linear-specific protocol. |
| `governance_parity_checklist_2026-03-07.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `governance_policy_engine_v1.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `interim-ai-technical-qa-cj-acceptance-policy-v1.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `isolation_mode_retirement_and_hardening_mapping_v1.md` | `temporal/active/tickets` | transitional | This appears operational but not clearly durable canon, so it should be reviewed in temporal storage first. |
| `legacy_backup_retirement_baseline_2026-03-07.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `legacy_identity_sweep_baseline_2026-03-09.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `legacy_identity_sweep_remediation_2026-03-09.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `linear-admin-change-control-v1.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `linear_bot_v1_runbook.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `linear_change_proposal_template_v1.md` | `protocol/templates` | canonical | Reusable template belongs in canonical protocol templates. |
| `linear_codex_deeplink_usage_policy_v1.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `linear_issue_template_evidence_contract_v1.md` | `protocol/templates` | canonical | Reusable template belongs in canonical protocol templates. |
| `linear_issue_template_evidence_contract_v2.md` | `protocol/templates` | canonical | Reusable template belongs in canonical protocol templates. |
| `linear-issue-workflow-reconfig-spec-v1.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `linear_link_reference_policy_v1.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `linear-operating-guide-changelog.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `linear_operating_guide_v1.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `linear_operating_guide_v2.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `linear_operating_guide_v3.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `live_cutover_auth_batch.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `local_remotes_validation_2026-03-07.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `long_thread_checkpoint_protocol_v1.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `memory_stewardship_service_contract_v1.md` | `protocol/agent-references` | canonical | Stable contract or agent-reference material belongs in canonical protocol references. |
| `minimum_phase4_agent_team_contract_v1.md` | `protocol/agent-references` | canonical | Stable contract or agent-reference material belongs in canonical protocol references. |
| `minimum_phase4_agent_team_execution_record_v1.md` | `temporal/active/tickets` | transitional | This appears operational but not clearly durable canon, so it should be reviewed in temporal storage first. |
| `minimum_phase4_agent_team_operating_matrix_v1.md` | `temporal/active/tickets` | transitional | This appears operational but not clearly durable canon, so it should be reviewed in temporal storage first. |
| `minimum_phase4_agent_team_readiness_v1.md` | `temporal/active/tickets` | transitional | This appears operational but not clearly durable canon, so it should be reviewed in temporal storage first. |
| `org_profile_ui_finish_checklist_2026-03-07.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `personal_github_exposure_baseline_2026-03-07.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `personal_github_lockdown_execution_checklist_2026-03-07.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `phase4_real_multi_agent_team_acceptance_contract_v1.md` | `protocol/agent-references` | canonical | Stable contract or agent-reference material belongs in canonical protocol references. |
| `phase4_return_sequence_post_taylor01_2026-03-12.md` | `temporal/active/tickets` | transitional | This appears operational but not clearly durable canon, so it should be reviewed in temporal storage first. |
| `post_bootstrap_hardening_runbook_v1.md` | `temporal/active/ticket__BIT-32` | temporal | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `post_ui_validation_command_bundle_2026-03-07.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `pre_rename_execution_branch_map_v1.md` | `temporal/active/tickets` | transitional | This appears operational but not clearly durable canon, so it should be reviewed in temporal storage first. |
| `qa_authority_model_v1.md` | `protocol/agent-references` | canonical | Stable contract or agent-reference material belongs in canonical protocol references. |
| `specialist_agent_registry_v1.md` | `protocol/agent-references` | canonical | Stable contract or agent-reference material belongs in canonical protocol references. |
| `specialist_operating_lanes_proof_v1.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `stage4_5_agent_stack_execution_plan_v1.md` | `temporal/active/tickets` | transitional | This appears operational but not clearly durable canon, so it should be reviewed in temporal storage first. |
| `startup_operating_model_v1.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `startup_operating_model_v2.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `startup_readiness_status_2026-03-12.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `t3_macmini_readiness_gate_v1.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `t3_pre_macmini_blockers_2026-03-15.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `taylor01_active_bypass_register_v1.md` | `temporal/active/tickets` | transitional | This appears operational but not clearly durable canon, so it should be reviewed in temporal storage first. |
| `taylor01_backlog_seed_v1.md` | `temporal/active/tickets` | transitional | This appears operational but not clearly durable canon, so it should be reviewed in temporal storage first. |
| `taylor01_boundary_map_v1.md` | `protocol/agent-references` | canonical | Stable contract or agent-reference material belongs in canonical protocol references. |
| `taylor01_coupling_log_v1.md` | `protocol/agent-references` | canonical | Stable contract or agent-reference material belongs in canonical protocol references. |
| `taylor01_north_star_v1.md` | `protocol/agent-references` | canonical | Stable contract or agent-reference material belongs in canonical protocol references. |
| `taylor01_portability_review_gate_v1.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `taylor01_repo_boundary_recommendation_v1.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
| `taylor_discord_general_intake_contract_v1.md` | `protocol/agent-references` | canonical | Stable contract or agent-reference material belongs in canonical protocol references. |
| `taylor_orchestrator_contract_v1.md` | `protocol/agent-references` | canonical | Stable contract or agent-reference material belongs in canonical protocol references. |
| `taylor_orchestrator_operational_proof_v1.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `taylor_real_agent_acceptance_contract_v1.md` | `protocol/agent-references` | canonical | Stable contract or agent-reference material belongs in canonical protocol references. |
| `taylor_runtime_core_contract_v1.md` | `protocol/agent-references` | canonical | Stable contract or agent-reference material belongs in canonical protocol references. |
| `team_session_platform_migration_contract_v1.md` | `protocol/agent-references` | canonical | Stable contract or agent-reference material belongs in canonical protocol references. |
| `ui_blocker_micro_checklist_bit54_bit55_2026-03-07.md` | `temporal/active/tickets` | transitional | This appears operational but not clearly durable canon, so it should be reviewed in temporal storage first. |
| `vera_qa_lane_contract_v1.md` | `protocol/agent-references` | canonical | Stable contract or agent-reference material belongs in canonical protocol references. |
| `vera_qa_lane_operational_proof_v1.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `vera_runtime_behavior_inventory_from_zulip_v1.md` | `temporal/active/tickets` | historical | Dated evidence, backup, checkpoint, or status material is non-canonical and belongs in temporal storage pending project grouping. |
| `vera_runtime_minimum_v1.md` | `protocol/agent-references` | canonical | Stable contract or agent-reference material belongs in canonical protocol references. |
| `workspace_local_state_location_policy_v1.md` | `protocol/configs` | canonical | Durable operating policy, spec, guide, or workflow rule belongs in canonical protocol configs. |
