document.addEventListener('DOMContentLoaded', () => {
    // Simulate real-time data updates for the hackathon demo
    const densityVal = document.getElementById('density-val');
    const riskVal = document.getElementById('risk-val');
    const criticalZone = document.querySelector('.zone.critical');

    setInterval(() => {
        // Fluctuate density between 80% and 95%
        const newDensity = Math.floor(Math.random() * 15) + 80;
        densityVal.textContent = newDensity + '%';

        if (newDensity > 90) {
            densityVal.style.color = 'var(--critical)';
            riskVal.textContent = 'CRITICAL';
            criticalZone.style.transform = 'scale(1.5)';
            criticalZone.style.opacity = '0.8';
        } else {
            densityVal.style.color = 'var(--text)';
            riskVal.textContent = 'Elevated';
            riskVal.style.color = 'var(--warning)';
            criticalZone.style.transform = 'scale(1)';
            criticalZone.style.opacity = '0.4';
        }
    }, 2000);
});
