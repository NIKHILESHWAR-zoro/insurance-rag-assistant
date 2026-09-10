const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function handle(res) {
  if (!res.ok) {
    let detail = 'Something went wrong.';
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch (_) {}
    throw new Error(detail);
  }
  return res.json();
}

export async function uploadPolicy(file) {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`${BASE_URL}/api/policies/upload`, {
    method: 'POST',
    body: form,
  });
  return handle(res);
}

export async function listPolicies() {
  const res = await fetch(`${BASE_URL}/api/policies`);
  return handle(res);
}

export async function deletePolicy(policyId) {
  const res = await fetch(`${BASE_URL}/api/policies/${policyId}`, { method: 'DELETE' });
  return handle(res);
}

export async function askQuestion(question, policyIds) {
  const res = await fetch(`${BASE_URL}/api/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, policy_ids: policyIds && policyIds.length ? policyIds : null }),
  });
  return handle(res);
}

export async function comparePolicies(question, policyIds) {
  const res = await fetch(`${BASE_URL}/api/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, policy_ids: policyIds }),
  });
  return handle(res);
}
