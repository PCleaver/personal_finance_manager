// Function to toggle between dark and light mode
function toggleTheme() {
    const body = document.body;
    const button = document.getElementById("theme-toggle-btn");

    // Toggle the dark-mode class on the body
    body.classList.toggle('dark-mode');

    // Change button text based on the current theme
    if (body.classList.contains('dark-mode')) {
        button.textContent = "Switch to Light Mode";
        localStorage.setItem('theme', 'dark');
    } else {
        button.textContent = "Switch to Dark Mode";
        localStorage.setItem('theme', 'light');
    }
}

// Sample Chart.js configuration
const ctx = document.getElementById('spendingChart').getContext('2d');
const spendingChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['Groceries', 'Rent', 'Fitness', 'Entertainment', 'Utilities'],  // Example labels
        datasets: [{
            label: 'Total Spending (£)',
            data: [200, 1200, 50, 300, 150], // Example data for each category
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        scales: {
            x: {
                ticks: {
                    autoSkip: false,   // Ensures all labels are shown without skipping
                    maxRotation: 45,   // Rotate labels if necessary to avoid overlapping
                    minRotation: 0,    // Ensure minimum rotation is zero for better alignment
                    padding: 10        // Add some padding for better spacing
                }
            },
            y: {
                beginAtZero: true,
                ticks: {
                    stepSize: 100,   // Adjust step size for better readability
                    padding: 10
                }
            }
        },
        layout: {
            padding: {
                left: 10,
                right: 10,
                top: 10,
                bottom: 30   // Increased bottom padding for better visibility of labels
            }
        },
        plugins: {
            legend: {
                position: 'top',
            }
        }
    }
});

// Check localStorage for theme preference and apply it on page load
window.onload = function() {
    const theme = localStorage.getItem('theme');
    if (theme === 'dark') {
        document.body.classList.add('dark-mode');
        document.getElementById("theme-toggle-btn").textContent = "Switch to Light Mode";
    }
}

