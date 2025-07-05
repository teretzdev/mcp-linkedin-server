// Utility functions for Applications

export function filterApplications(jobs, searchTerm, statusFilter) {
  let filtered = jobs;
  if (searchTerm) {
    filtered = filtered.filter(job =>
      (job.title || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (job.company || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (job.location || '').toLowerCase().includes(searchTerm.toLowerCase())
    );
  }
  if (statusFilter !== 'all') {
    filtered = filtered.filter(job => job.status === statusFilter);
  }
  return filtered;
}

export function sortApplications(jobs, sortBy, sortOrder) {
  const sorted = [...jobs];
  sorted.sort((a, b) => {
    let aValue = a[sortBy];
    let bValue = b[sortBy];
    if (sortBy === 'date_applied') {
      aValue = new Date(aValue);
      bValue = new Date(bValue);
    }
    if (sortOrder === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });
  return sorted;
}

export function getApplicationsAnalytics(jobs) {
  const total = jobs.length;
  const statusCounts = {};
  const monthlyCounts = {};
  jobs.forEach(job => {
    statusCounts[job.status] = (statusCounts[job.status] || 0) + 1;
    const date = new Date(job.date_applied);
    const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
    monthlyCounts[monthKey] = (monthlyCounts[monthKey] || 0) + 1;
  });
  return { total, statusCounts, monthlyCounts };
}

export function exportApplicationsCSV(jobs) {
  return () => {
    const csvContent = [
      ['Title', 'Company', 'Location', 'Status', 'Date Applied', 'Notes'],
      ...jobs.map(job => [
        job.title || '',
        job.company || '',
        job.location || '',
        job.status || '',
        job.date_applied || '',
        (job.notes || []).map(note => note.text).join('; ')
      ])
    ].map(row => row.map(field => `"${field}"`).join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `applications-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };
} 