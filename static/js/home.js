
const playersDiv = document.getElementById('players');
const searchButton = document.getElementById('searchButton');
const playerSearchTextBox = document.getElementById('playerSearchTextBox');
const playerListBtn = document.getElementsByClassName('playerListBtn');

searchButton.addEventListener('click', function () {
    let xhr = new XMLHttpRequest();
    xhr.onload = function () {
        if(xhr.status >= 200 && xhr.status < 300) {
            let players = JSON.parse(xhr.responseText);
            if(players.length === 1) {
                window.location.href = '/players/' + playerSearchTextBox.value + '/stats'
            }else {
                players.forEach(function (player) {
                    playersDiv.innerHTML += '<div class="playerListBtn"><button class="listPlayerSpan">' + player['full_name'] + '</button></div>'
                });
                updateListButtons()
            }
        } else {
            console.log("Error: " + xhr.status.toString());
        }
    };

    xhr.open('GET', '/players/list?name=' + playerSearchTextBox.value);
    xhr.send();
});

function updateListButtons() {
    for(let i = 0; i < playerListBtn.length; i++) {
    playerListBtn[i].addEventListener('click', function () {
        const player = this.innerText;
        window.location.href = '/players/' + player + '/stats'
    });
}
}