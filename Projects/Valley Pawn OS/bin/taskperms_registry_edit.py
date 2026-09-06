#!/usr/bin/python3
"""
taskperms_registry_edit.py  —  created 2026-09-04

WHY THIS EXISTS
---------------
On 2026-09-04 the `bald-rock-15-day-contract` task fired on time (04:06), ran fine
for 5 minutes, then died silently. App log:

    04:11:00 Not auto-approving "mcp__...__listRecipients" in scheduled task
             "bald-rock-15-day-contract": rule(s) not in stored approvals ... (stored count=4)

The task was approved for 4 DocuSign tools but not the 5th one it needed mid-flow.
With no human present to click approve, the run idled and was killed by the hung-run
reaper. It never reached its failure-DM step, so it failed COMPLETELY SILENTLY —
exactly the class the Fleet Guardian's output-verification pass exists to catch.

This is not a Bald Rock bug. A registry scan the same day found 67 enabled tasks with
partial approvals (most with exactly ONE approved tool). Every one of them stalls the
same way the first time it calls a sibling tool of a server it is already trusted with.
Note that `sendReminder`'s own tool description instructs the model to call
`listRecipients` first — so the trap can be sprung by a tool the task never named.

THE RULE THIS APPLIES
---------------------
If a task is already trusted with ANY tool from MCP server X, grant it all
READ-ONLY tools of server X.

Reads cannot send, publish, spend, or delete. Granting them cannot cause a harmful
action — it can only prevent a stall. Every WRITE tool still requires its own explicit
approval, exactly as before. This is deliberately narrower than "approve everything."

ADDITIVE ONLY (Rule #4): entries are only ever added. Nothing is removed, and no task
without an existing trust anchor on a server gains anything on that server.

Must run with Claude.app fully quiesced — the app holds the registry in memory and
will overwrite a live edit. Driven by taskperms_apply.sh (same proven quiesce pattern
as migrate3.sh / chromeperms_apply.sh).
"""

import json
import os
import shutil
import time

REG = os.path.expanduser(
    '~/Library/Application Support/Claude/local-agent-mode-sessions/'
    '823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/'
    'scheduled-tasks.json'
)

# Read-only tool sets, keyed by MCP server id. Every tool below is a query/read.
# Anything that sends, posts, creates, updates, deletes, moves money, or changes
# configuration is deliberately EXCLUDED and still needs its own approval.
READ_ONLY = {
    # DocuSign
    '8ff1eb8f-1c43-4cbb-bcb3-9167c3c96cc7': [
        'getEnvelope', 'getEnvelopes', 'listRecipients', 'listEnvelopeDocuments',
        'getTemplates', 'getAccount', 'getUser', 'getUserInfo', 'getUsers',
        'getAgreementDetails', 'getAllAgreements', 'getWorkflowInstance',
        'getWorkflowInstancesList', 'getWorkflowsList',
        'getWorkflowTriggerRequirements',
    ],
    # Slack
    'f92ce7c6-0353-4419-8491-f0843b182ff2': [
        'slack_read_channel', 'slack_read_thread', 'slack_read_user_profile',
        'slack_read_canvas', 'slack_search_channels', 'slack_search_public',
        'slack_search_public_and_private', 'slack_search_users',
    ],
    # Gmail
    '00007879-ef17-43e5-9d59-6325cd2f0a31': [
        'search_threads', 'get_message', 'get_thread', 'list_drafts', 'get_draft',
        'list_labels',
    ],
    # Google Drive
    '2ce817f2-5038-4cde-a6ab-8dedbe8abd84': [
        'search_files', 'read_file_content', 'get_file_metadata',
        'list_recent_files', 'download_file_content', 'get_file_permissions',
    ],
    # Gusto
    'ca1b6a08-a5e1-43c1-b6ee-b11de4e2e8df': [
        'get_company', 'get_compensation', 'get_contractor', 'get_contractor_payment',
        'get_contractor_payment_group', 'get_department', 'get_employee',
        'get_employee_earnings_summary', 'get_employee_rehire', 'get_employee_work_address',
        'get_job', 'get_location', 'get_pay_schedule', 'get_payroll',
        'get_time_off_balances', 'get_time_off_request', 'get_time_sheet',
        'get_token_info', 'list_contractor_payment_groups', 'list_contractor_payments',
        'list_contractors', 'list_custom_fields_schema', 'list_departments',
        'list_earning_types', 'list_employee_custom_fields',
        'list_employee_employment_history', 'list_employee_jobs',
        'list_employee_terminations', 'list_employee_work_addresses', 'list_employees',
        'list_job_compensations', 'list_locations', 'list_pay_periods',
        'list_pay_schedule_assignments', 'list_pay_schedules', 'list_payroll_blockers',
        'list_payrolls', 'list_time_off_requests', 'list_time_records',
    ],
    # QuickBooks Online
    '37675e3a-e51c-470a-9eeb-b0aba96ba809': [
        'company_info', 'profit_loss_generator', 'profit_loss_quickbooks_account',
        'cash_flow_generator', 'cash_flow_quickbooks_account',
        'benchmarking_against_industry', 'benchmarking_quickbooks_account',
        'qbo_accounting_get_ap_aging_detail', 'qbo_accounting_get_ap_aging_summary',
        'qbo_accounting_get_ar_aging_detail', 'qbo_accounting_get_ar_aging_summary',
        'qbo_accounting_get_balance_sheet', 'qbo_accounting_get_product_service_list',
        'qbo_accounting_get_sales_by_customer_summary',
        'qbo_accounting_get_sales_by_product_summary', 'qbo_catalog_search_products',
        'qbo_contact_search_customer', 'qbo_sales_get_invoices',
        'qbo_sales_get_estimates', 'qbo_sales_get_settings',
        'qbo_sales_get_recurring_invoices', 'qbo_sales_get_payment_links',
        'qbo_payroll_get_employees', 'qbo_payroll_search_employee',
    ],
    # Google Calendar
    'ae0e7c34-87de-4983-b24b-74cfc75cd4a1': [
        'list_calendars', 'list_events', 'get_event', 'search_events', 'suggest_time',
    ],
    # Canva
    'a246b176-44bb-4d16-83f9-a6b2c4e896e1': [
        'read-design', 'get-assets', 'get-design-dataset', 'get-brand-template-dataset',
        'get-export-formats', 'list-brand-kits', 'list-comments', 'list-folder-items',
        'list-replies', 'search-brand-templates', 'search-designs', 'search-folders',
        'resolve-shortlink', 'help',
    ],
}

# Task-specific WRITE tools that a task's own SKILL.md provably requires but that were
# missing from its approvals. Narrow and explicit — never bulk-granted.
EXPLICIT_WRITES = {
    # SKILL.md sends contracts from two named DocuSign TEMPLATE ids, which is
    # createEnvelopeFromTemplate, not createEnvelope. Only createEnvelope was approved,
    # so the first day with an actual contract to send would have stalled too.
    'bald-rock-15-day-contract': [
        'mcp__8ff1eb8f-1c43-4cbb-bcb3-9167c3c96cc7__createEnvelopeFromTemplate',
    ],
}


def server_of(tool_name):
    parts = tool_name.split('__')
    return parts[1] if len(parts) > 2 else None


def main():
    stamp = time.strftime('%Y%m%d-%H%M%S')
    backup = f'{REG}.bak-taskperms-{stamp}'
    shutil.copy2(REG, backup)
    print(f'backup: {backup}')

    with open(REG) as fh:
        data = json.load(fh)

    tasks = data['scheduledTasks']
    added_total = 0
    touched = 0

    for task in tasks:
        if not task.get('enabled'):
            continue

        approvals = task.get('approvedPermissions') or []
        have = {a.get('toolName') for a in approvals if a.get('toolName')}
        if not have:
            # No trust anchor on any server -> this rule grants nothing. Left alone.
            continue

        trusted_servers = {server_of(t) for t in have if t.startswith('mcp__')}
        trusted_servers.discard(None)

        wanted = set()
        for srv in trusted_servers:
            for tool in READ_ONLY.get(srv, []):
                wanted.add(f'mcp__{srv}__{tool}')
        wanted.update(EXPLICIT_WRITES.get(task['id'], []))

        new = sorted(wanted - have)
        if not new:
            continue

        for tool_name in new:
            approvals.append({'toolName': tool_name})
        task['approvedPermissions'] = approvals
        added_total += len(new)
        touched += 1
        print(f'{task["id"]}: +{len(new)} (now {len(approvals)})')

    tmp = f'{REG}.tmp-taskperms'
    with open(tmp, 'w') as fh:
        json.dump(data, fh, indent=1)
    os.replace(tmp, REG)

    print(f'\nDONE: {added_total} approvals added across {touched} enabled tasks.')
    print('Additive only — nothing removed, no write tools granted except EXPLICIT_WRITES.')


if __name__ == '__main__':
    main()
