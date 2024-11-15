document.getElementById('gachaButton').addEventListener('click', function() {
    fetch('/draw_single')
        .then(response => response.json())
        .then(data => {
            updateResult(data);
        });
});

document.getElementById('11gachaButton').addEventListener('click', function() {
    fetch('/draw_eleven')
        .then(response => response.json())
        .then(data => {
            updateResult(data);
        });
});

document.getElementById('resetButton').addEventListener('click', function() {
    fetch('/reset')
        .then(response => response.json())
        .then(data => {
            updateResult(data);
            document.getElementById('srPlusCostResult').innerHTML = ''; 
        });
});

document.getElementById('srPlusCostButton').addEventListener('click', function() {
    fetch('/calculate_sr_plus_cost')
        .then(response => response.json())
        .then(data => {
            const resultDiv = document.getElementById('srPlusCostResult');
            resultDiv.innerHTML = `全種類のSR+が出るまでかかる費用は ${data.cost} 円で、かかる回数は ${data.draws} 回です。`;
        });
});

function updateResult(data) {
    document.getElementById('totalCount').textContent = data.totalDraws;
    document.getElementById('totalSpent').textContent = data.totalCost;
    const cardList = document.getElementById('cardList');
    cardList.innerHTML = '';
    for (const [card, count] of Object.entries(data.cardCounts)) {
        const li = document.createElement('li');
        li.textContent = `${card}: ${count}`;
        cardList.appendChild(li);
    }
    const cardResultDiv = document.getElementById('cardResult');
    cardResultDiv.innerHTML = '';
    data.cards.forEach(card => {
        const img = document.createElement('img');
        img.src = card.image;
        cardResultDiv.appendChild(img);
    });
}