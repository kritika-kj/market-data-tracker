let navChart;

const roleContent = {
  admin: {
    title: 'Admin dashboard',
    description: 'Manage access and monitor the market data workspace.'
  },
  analyst: {
    title: 'Analyst dashboard',
    description: 'Explore NAV history and prepare useful market insights.'
  },
  viewer: {
    title: 'NAV viewer',
    description: 'Review stored NAV history and recent values.'
  }
};

async function loadSession() {
  const response = await fetch('/api/session');
  if (!response.ok) {
    window.location.href = '/';
    return null;
  }
  return response.json();
}

async function loadNav() {
  const schemeCode = document.querySelector('#scheme-code').value.trim();
  const status = document.querySelector('#data-status');
  status.textContent = 'Loading...';
  const response = await fetch(`/api/nav-summary?scheme_code=${encodeURIComponent(schemeCode)}`);
  const data = await response.json();
  if (!response.ok) {
    if (navChart) {
      navChart.destroy();
      navChart = null;
    }
    document.querySelector('#fund-name').textContent = 'NAV history';
    document.querySelector('#latest-nav').textContent = '-';
    document.querySelector('#lowest-nav').textContent = '-';
    document.querySelector('#highest-nav').textContent = '-';
    document.querySelector('#nav-table').innerHTML = '';
    status.textContent = data.error || 'Unable to load data';
    return;
  }

  document.querySelector('#fund-name').textContent = data.scheme_name;
  const recent = data.values.slice(-5).reverse();
  const recentLabels = data.labels.slice(-5).reverse();
  document.querySelector('#latest-nav').textContent = data.values.at(-1)?.toFixed(6) || '-';
  document.querySelector('#lowest-nav').textContent = data.values.length ? Math.min(...data.values).toFixed(6) : '-';
  document.querySelector('#highest-nav').textContent = data.values.length ? Math.max(...data.values).toFixed(6) : '-';
  document.querySelector('#nav-table').innerHTML = recent.map((value, index) => `<tr><td>${recentLabels[index]}</td><td>${value.toFixed(6)}</td></tr>`).join('');

  if (navChart) navChart.destroy();
  navChart = new Chart(document.querySelector('#nav-chart'), {
    type: 'line',
    data: { labels: data.labels, datasets: [{ label: 'NAV', data: data.values, borderColor: '#0c6b66', backgroundColor: 'rgba(12, 107, 102, 0.12)', fill: true, pointRadius: 0, tension: 0.2 }] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
  });
  status.textContent = `${data.values.length} records`;
}

async function loadUsers() {
  const response = await fetch('/api/admin/users');
  if (!response.ok) return;
  const data = await response.json();
  document.querySelector('#user-table').innerHTML = data.users.map((user) => `
    <tr><td>${user.email}</td><td>${user.role}</td><td>${user.created_at.slice(0, 10)}</td></tr>
  `).join('');
}

async function startDashboard() {
  const session = await loadSession();
  if (!session) return;
  const { user } = session;
  const copy = roleContent[user.role];
  document.querySelector('#user-name').textContent = user.email;
  document.querySelector('#user-role').textContent = user.role;
  document.querySelector('#dashboard-title').textContent = copy.title;
  document.querySelector('#dashboard-description').textContent = copy.description;
  document.querySelector('#admin-panel').hidden = user.role !== 'admin';
  document.querySelector('#analyst-panel').hidden = user.role !== 'analyst';
  if (user.role === 'admin') {
    await loadUsers();
  }
  await loadNav();
}

document.querySelector('#load-data').addEventListener('click', loadNav);
document.querySelector('#create-user-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const data = Object.fromEntries(new FormData(form));
  const response = await fetch('/api/admin/users', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  const result = await response.json();
  const message = document.querySelector('#admin-message');
  message.textContent = result.error || result.message;
  message.classList.toggle('error', !response.ok);
  if (response.ok) {
    form.reset();
    await loadUsers();
  }
});
document.querySelector('#logout-button').addEventListener('click', async () => {
  await fetch('/api/logout', { method: 'POST' });
  window.location.href = '/';
});
startDashboard();
