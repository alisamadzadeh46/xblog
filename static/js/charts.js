/* XBlog — charts.js */
document.addEventListener('DOMContentLoaded', () => {
  const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
  const gridC  = isDark ? 'rgba(255,255,255,.04)' : 'rgba(0,0,0,.05)';
  const textC  = isDark ? '#71767b' : '#8b98a5';

  if (!window.Chart) return;
  Chart.defaults.font.family = "'Geist', sans-serif";
  Chart.defaults.color = textC;
  Chart.defaults.borderColor = isDark ? '#2f3336' : '#e7e9ea';

  const tip = {
    backgroundColor: isDark ? '#16181c' : '#fff',
    borderColor: isDark ? '#2f3336' : '#e7e9ea',
    borderWidth: 1,
    titleColor: isDark ? '#e7e9ea' : '#0f1419',
    bodyColor: textC,
    padding: 10,
  };

  // Views line chart
  const vc = document.getElementById('xViewsChart');
  if (vc && window.viewsData) {
    new Chart(vc, {
      type: 'line',
      data: {
        labels: viewsData.map(d => d.d),
        datasets: [{ label: 'Views', data: viewsData.map(d => d.n),
          borderColor: '#1d9bf0', backgroundColor: 'rgba(29,155,240,.08)',
          borderWidth: 2, pointRadius: 3, pointHoverRadius: 5,
          fill: true, tension: 0.4 }]
      },
      options: {
        responsive: true, plugins: { legend: { display: false }, tooltip: tip },
        scales: {
          x: { grid: { color: gridC }, ticks: { maxTicksLimit: 7 } },
          y: { grid: { color: gridC }, beginAtZero: true, ticks: { precision: 0 } }
        }
      }
    });
  }

  // Category doughnut
  const cc = document.getElementById('xCatChart');
  if (cc && window.catData) {
    const pal = ['#1d9bf0','#00ba7c','#ffd400','#f4212e','#7856ff','#ff7a00'];
    new Chart(cc, {
      type: 'doughnut',
      data: {
        labels: catData.map(d => d.l),
        datasets: [{ data: catData.map(d => d.n),
          backgroundColor: pal,
          borderColor: isDark ? '#000' : '#fff',
          borderWidth: 3, hoverOffset: 8 }]
      },
      options: {
        responsive: true, cutout: '68%',
        plugins: {
          legend: { position: 'bottom', labels: { padding: 14, usePointStyle: true, pointStyleWidth: 8 } },
          tooltip: tip
        }
      }
    });
  }

  // Analytics bar chart
  const ac = document.getElementById('xAnalyticsChart');
  if (ac && window.viewsData) {
    new Chart(ac, {
      type: 'bar',
      data: {
        labels: viewsData.map(d => d.d),
        datasets: [{ label: 'Views', data: viewsData.map(d => d.n),
          backgroundColor: 'rgba(29,155,240,.15)', borderColor: '#1d9bf0',
          borderWidth: 1, borderRadius: 3 }]
      },
      options: {
        responsive: true, plugins: { legend: { display: false }, tooltip: tip },
        scales: {
          x: { grid: { color: gridC } },
          y: { grid: { color: gridC }, beginAtZero: true, ticks: { precision: 0 } }
        }
      }
    });
  }
});
