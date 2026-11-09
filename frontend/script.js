let currentUser = null;
const API_URL = 'http://127.0.0.1:8000';
async function loginUser() {
    const username = document.getElementById('usernameInput').value;
    if (!username) return alert('Введите имя!');
    try {
        const response = await fetch(`${API_URL}/api/users`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username })
        });
        if (!response.ok) {
            const errorData = await response.json();
            return alert(errorData.detail || 'Ошибка при входе!');
        }
        currentUser = await response.json();
        document.getElementById('userNameDisplay').textContent = currentUser.username;
        document.getElementById('balanceDisplay').textContent = currentUser.balance;

        document.getElementById('authSection').classList.add('hidden');
        document.getElementById('bankSection').classList.remove('hidden');

        loadTransactions();
    } catch (error) {
        alert('Ошибка соединения с сервером!');
    }
}
async function makeTransaction(type) {
    const amount = parseFloat(document.getElementById('amountInput').value);
    if (!amount || amount <= 0) return alert('Введите корректную сумму!');
    const endpoint = type === 'deposit' ? '/api/deposit' : '/api/withdraw';

    try {
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: currentUser.id, amount })
        });

        const data = await response.json();
        if (response.ok) {
            currentUser.balance = data.new_balance;
            document.getElementById('balanceDisplay').textContent = currentUser.balance;
            document.getElementById('amountInput').value = '';
            loadTransactions();
        } else {
            alert(data.detail);
        }
    } catch (error) {
        alert('Ошибка соединения с сервером!');
    }
}
async function loadTransactions() {
    try {
        const response = await fetch(`${API_URL}/api/transactions/${currentUser.id}`);
        if (!response.ok) {
            return alert('Ошибка загрузки транзакций!');
        }
        const txs = await response.json();
        const txList = document.getElementById('txList');
        txList.innerHTML = '';
        txs.reverse().forEach(tx => {
            const li = document.createElement('li');
            li.textContent = `${tx.type}: ${tx.amount}тг (${new Date(tx.timestamp).toLocaleTimeString()})`;
            txList.appendChild(li);
        });
    } catch (error) {
        alert('Ошибка соединения с сервером!');
    }
}