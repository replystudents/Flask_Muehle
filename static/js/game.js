let svg = d3.select("svg#game")


let coordinateOffsetX
let coordinateOffsetY
let coordinateFactorX
let coordinateFactorY
setFactorOffset()

function setFactorOffset() {
    coordinateOffsetX = document.getElementById("game").getBoundingClientRect().x
    coordinateOffsetY = document.getElementById("game").getBoundingClientRect().y
    coordinateFactorX = document.getElementById("game").getBoundingClientRect().width / svg.attr('viewBox').split(' ')[3]
    coordinateFactorY = document.getElementById("game").getBoundingClientRect().height / svg.attr('viewBox').split(' ')[2]

}

window.addEventListener('resize', () => {
    setFactorOffset()
})

let stones = {'player1': [], 'player2': []}

let iStones = {player1: 0, player2: 0}
let player;
let enemyplayer;

svg.on('click', function () {
    if (gamedata.state === 'PLACE_PHASE') {
        // if (players["player1"].length < 9 || players["player2"].length < 9) {
        // let player = players["player2"].length < players["player1"].length ? 'player2' : 'player1';

        let mouse = d3.mouse(this);
        let elem = document.elementFromPoint(mouse[0] * coordinateFactorX + coordinateOffsetX, mouse[1] * coordinateFactorY + coordinateOffsetY);
        if (elem.classList.contains("dot")) {
            let pos = elem.id.split('-')

            console.log(pos)
            placeTokenOnBoard(pos[1], pos[2])
            // addStone()
        }
        // } else {
        //     placingPhase = false;
        // }
    } else if (gamedata.state === 'MILL') {
        let mouse = d3.mouse(this);
        let elem = document.elementFromPoint(mouse[0] * coordinateFactorX + coordinateOffsetX, mouse[1] * coordinateFactorY + coordinateOffsetY);
        if (elem.classList.contains("player") && !elem.classList.contains(player)) {
            removeTokenFromBoard(elem.id.split('-')[1], elem.id)
        }

        // if (hasMuehle === true) {
        //     let player = 'player1'
        //
        //     if (current.classList.contains(player)) {
        //         removeStone()
        //     }
        // }
    }


})

function addStone(playername, pos_x, pos_y) {
    let pos = document.getElementById('pos-' + pos_x + '-' + pos_y)
    console.log('pos-' + pos_x + '-' + pos_y)
    console.log(pos)
    let stone;
    if (playername === player) {
        stone = svg.append("circle")
            .attr('id', `${playername}-${iStones[playername]++}`)
            .attr('class', `player draggable ${playername}`)
            .attr("cx", pos.getAttribute('cx'))
            .attr("cy", pos.getAttribute('cy'))
            .attr("r", 30)
        dragHandler(stone);
    } else {
        stone = svg.append("circle")
            .attr('id', `${playername}-${iStones[playername]++}`)
            .attr('class', `player ${playername}`)
            .attr("cx", pos.getAttribute('cx'))
            .attr("cy", pos.getAttribute('cy'))
            .attr("r", 30)
    }

    // .on('contextmenu', function () {
    //     d3.event.preventDefault()
    //     removeStone();
    // });

    // if (player === 'player1') {
    //     players["player1"].push(stone)
    // } else {
    //     players["player2"].push(stone)
    // }

}

function removeStone(tokenid) {
    console.log('remove:' + tokenid)
    d3.select('circle#' + tokenid).remove()
}

let dragHandler = d3.drag()
    .on('drag', dragged)
    .on('start', dragstarted)
    .on('end', dragended);

let startposition = [];
let current;

function dragstarted() {
    if (gamedata.state === 'PLAYING_PHASE') {
        current = d3.select(this);
        current.style('cursor', 'grabbing')
        current.raise()
        startposition[0] = current.attr("cx")
        startposition[1] = current.attr("cy")
        //console.log("startposition", startposition)
    }
}

function dragged() {
    if (gamedata.state === 'PLAYING_PHASE') {
        current = d3.select(this);
        current
            .attr('cx', d3.event.x)
            .attr('cy', d3.event.y);
    }
}

function dragended() {
    if (gamedata.state === 'PLAYING_PHASE') {
        hideStone(true)
        current.style('cursor', 'grab')
        let mouse = d3.mouse(this);
        let elem = document.elementFromPoint(mouse[0] * coordinateFactorX + coordinateOffsetX, mouse[1] * coordinateFactorY + coordinateOffsetY);
        //console.log(elem)
        //console.log("mouse",mouse)
        hideStone(false)


        if (elem.classList.contains("dot")) {
            let pos = elem.id.split('-')
            moveToken(current.attr('id'), pos[1], pos[2])
            current
                .attr('cx', startposition[0])
                .attr('cy', startposition[1]);
            // current
            //     .attr('cx', Math.round(d3.event.x / 50) * 50)
            //     .attr('cy', Math.round(d3.event.y / 50) * 50);
        } else {
            current
                .attr('cx', startposition[0])
                .attr('cy', startposition[1]);
        }

    }
}

function moveStone(playername, tokenid, pos_x, pos_y) {
    let token = d3.select('circle#' + tokenid)
    let dot = d3.select('circle#pos-' + pos_x + '-' + pos_y)
    console.log('token')
    console.log(token)
    console.log('dot')
    console.log(dot)
    token
        .attr('cx', dot.attr('cx'))
        .attr('cy', dot.attr('cy'))
}

function hideStone(hide) {
    if (hide) {
        current.attr('style', 'display:none;')
    } else {
        current.attr('style', 'display:inline;')
    }
}

/**
 svg.on("mousemove", function() {
    let mouse = d3.mouse(this);
    let elem = document.elementFromPoint(mouse[0], mouse[1]);
    console.log(elem)
})
 */

function placeStone() {

}

function startGame() {
    var modal = document.getElementById("waitingpopup");
    modal.style.display = "none";

    let enemyName = document.getElementById('enemyName')
    if (gamedata.player1 === username) {
        player = 'player1'
        enemyplayer = 'player2'
        enemyName.innerText = enemyName.innerText + ' ' + gamedata.player2
    } else {
        player = 'player2'
        enemyplayer = 'player1'
        enemyName.innerText = enemyName.innerText + ' ' + gamedata.player1
    }

    nextMove()
}


function nextMove() {
    let dots = d3.selectAll('circle.dot')
    let ownstones = d3.selectAll('circle.player1')
    let enemystones = d3.selectAll('circle.player2')
    if (gamedata.activePlayer === username) {
        ownstones = d3.selectAll('circle.' + player)
        enemystones = d3.selectAll('circle.' + enemyplayer)
        switch (gamedata.state) {
            case 'PLACE_PHASE':
                dots.style('cursor', 'pointer')
                ownstones.style('cursor', 'not-allowed')
                enemystones.style('cursor', 'not-allowed')
                break;
            case 'PLAYING_PHASE':
                dots.style('cursor', 'not-allowed')
                ownstones.style('cursor', 'grab')
                enemystones.style('cursor', 'not-allowed')
                break;
            case 'MILL':
                dots.style('cursor', 'not-allowed')
                ownstones.style('cursor', 'not-allowed')
                enemystones.style('cursor', 'pointer')
                break;
            case'END':
                dots.style('cursor', 'default')
                ownstones.style('cursor', 'default')
                enemystones.style('cursor', 'default')
                break;
            default:
                break;
        }
    } else {
        dots.style('cursor', 'not-allowed')
        ownstones.style('cursor', 'not-allowed')
        enemystones.style('cursor', 'not-allowed')
    }

    if (gamedata.state === 'END') {
        window.alert(gamedata.winner + ' hat gewonnen!')


        socket.emit('leave', {'room': gameid})


    }


    let enemyName = document.getElementById('enemyName')
    let ownName = document.getElementById('ownName')
    let border = document.getElementById('border')
    if (gamedata.activePlayer === username) {
        border.style.stroke = 'green'
        ownName.style.color = 'green'
        enemyName.style.color = 'black'
    } else {
        border.style.stroke = 'black'
        ownName.style.color = 'black'
        enemyName.style.color = 'green'
    }
    console.log('Gamestate: ' + gamedata.state)
}


let gameid = false;
let gameUrl = document.getElementById("gameUrl")
if (gameUrl) {
    gameUrl.value = window.location.href
    gameid = window.location.href.split('/')[4]
    console.log(gameid)
    gameUrl.onclick = function copyUrl() {

        /* Select the text field */
        gameUrl.select();
        gameUrl.setSelectionRange(0, 99999); /* For mobile devices */

        /* Copy the text inside the text field */
        document.execCommand("copy");

        /* Alert the copied text */
        // console.log("Copied the text: " + gameUrl.value);
    }
}
let username;
let gamedata;

let socket = io();
if (gameid) {
    socket.on('connect', function () {
        socket.emit('connected', {data: 'I\'m connected!'});

        socket.emit('join', {'gameid': gameid})
    });
}

socket.on('game', function (data) {
    username = data
})

socket.on('message', function (data) {
    console.log('message')
    console.log(data)
})

socket.on('json', function (json) {
    console.log('json')
    console.log(json)

})

socket.on('startGame', function (data) {
    gamedata = data;
    console.log(data)
    startGame()
})

socket.on('tokenPlaced', function (data) {
    gamedata = data
    console.log("TOKENPLACED")
    console.log(data)
    addStone(data.player, data.pos_x, data.pos_y)
    nextMove()
})

socket.on('ErrorPlacing', function (data) {
    gamedata = data
    console.log("ERROR Placing")
})


function placeTokenOnBoard(pos_x, pos_y) {
    socket.emit('placeTokenOnBoard', {
        'gameid': gameid,
        'player': player,
        'token': iStones[player],
        'pos_x': pos_x,
        'pos_y': pos_y
    })
}

socket.on('tokenMoved', function (data) {
    gamedata = data
    moveStone(data.player, data.tokenid, data.pos_x, data.pos_y)
    nextMove()
})
socket.on('ErrorMoving', function (data) {
    // if(gamedata.activePlayer === username) {
    //
    //     current
    //         .attr('cx', startposition[0])
    //         .attr('cy', startposition[1]);
    // }
    console.log("ERROR Moving")
})

function moveToken(token, pos_x, pos_y) {
    socket.emit('moveToken', {
        'gameid': gameid,
        'player': player,
        'token': token.split('-')[1],
        'tokenid': token,
        'pos_x': pos_x,
        'pos_y': pos_y
    })
}


function removeTokenFromBoard(token, tokenid) {
    socket.emit('removeToken', {
        'gameid': gameid,
        'player': player,
        'token': token,
        'tokenid': tokenid
    })
}

socket.on('tokenRemoved', function (data) {
    gamedata = data
    console.log('tokenRemoved')
    removeStone(data.tokenid)
    nextMove()
})


// console.log(coordinateFactorX, coordinateFactorY)

// svg.on('mousemove', function(){
//     let mouse = d3.mouse(this);
//     let elem = document.elementFromPoint((mouse[0])*coordinateFactorX, (mouse[1])*coordinateFactorY);
//     console.log(elem.id, "mouse", mouse)
// })

// let players = {player1: [], player2: []}
// let placingPhase = true;
// let hasMuehle = true;

// Get the modal
//
// // Get the <span> element that closes the modal
// var span = document.getElementsByClassName("close")[0];
//
//
// // When the user clicks on <span> (x), close the modal
// span.onclick = function () {
//     modal.style.display = "none";
// }
//
// // When the user clicks anywhere outside of the modal, close it
// // window.onclick = function (event) {
// //     if (event.target === modal) {
// //         modal.style.display = "none";
// //     }
// // }


// let circle = svg.append("circle")
//     .attr('class', 'player player1 draggable')
//     .attr("cx", 50)
//     .attr("cy", 50);
// let circle2 = svg.append("circle")
//     .attr('class', 'player player2 draggable')
//     .attr("cx", 150)
//     .attr("cy", 150);
//
// dragHandler(circle);
// dragHandler(circle2);
