
const strPlayer = document.getElementById('player').value;
const player = stringArrayToDictionary(strPlayer);

// loadHeaders();
loadPlots();

function loadPlots() {
    let xhr = new XMLHttpRequest();

    const regularSeason = document.getElementById('regular-season-plots');

    xhr.onload = function () {
        if(xhr.status >= 200 && xhr.status < 300) {

            const stats = JSON.parse(xhr.responseText);
            let titles = ["<h2> Regular Season Career Stats</h2>", "<h2> Playoffs Career Stats</h2>", "<h2> College Career Stats</h2>"];
            let tempHTML = "";
            for(let num in stats) {
                if(stats[num].length !== 0) {
                    tempHTML += titles[num];
                    for(let img in stats[num]) {
                        tempHTML += "<img class='plot-img' src='https://visualize-nba-stats.s3-us-west-2.amazonaws.com/" + stats[num][img] + "'>";
                    }
                    tempHTML += "<br/>"
                }
            }

            regularSeason.innerHTML = tempHTML;
        } else {
            console.log(xhr.error);
        }
    };

    xhr.open('GET', '/load/plots?id=' + player['id'] + '&name=' + player['full_name']);
    xhr.send()
}

function loadHeaders() {
    const headerContent = document.getElementById('header-top-content');

    let xhr = new XMLHttpRequest();

    xhr.onload = function () {
        if (xhr.status >= 200 && xhr.status < 300) {
            const playerInfo = JSON.parse(xhr.responseText);

            let tempHTML = "";
            let counter = 0;

            for(let key in playerInfo) {
                if(counter === 0) {
                    tempHTML += "<div>";
                } else if (counter === 11) {
                    tempHTML += "</div>";
                } else if (counter % 3 === 0) {
                    tempHTML += "</div><div>"
                }

                tempHTML += "<h5>" + key + ": " + playerInfo[key] + "</h5>";
                counter++;
            }

            headerContent.innerHTML = tempHTML;
        } else {
            console.log("Error: " + xhr.error);
        }
    };
    xhr.open('GET', '/load/headers?id=' + player['id']);
    xhr.send()
}

function stringArrayToDictionary(arr) {
    let dict = {};
    const temp = arr.slice(1, -1).replace(/'/g, "").replace(/, /g, ",").split(',');

    temp.forEach(function (pair) {
        const temp = pair.split(': ');
        dict[temp[0]] = temp[1];
    });
    console.log(dict);
    return dict;
}