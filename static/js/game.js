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

window.addEventListener('scroll', () => {
    setFactorOffset()
})

window.addEventListener('load', () => {
    setFactorOffset()
})

window.addEventListener('beforeunload', () => {
    socket.emit('leave', {'room': gameid})
})

let player;
let enemyplayer;

svg.on('click', function () {
    setFactorOffset()
    if (gamedata) {
        if (gamedata.activePlayer === username) {
            if (gamedata.state === 'PLACE_PHASE') {
                let mouse = d3.mouse(this);
                let elem = document.elementFromPoint(mouse[0] * coordinateFactorX + coordinateOffsetX, mouse[1] * coordinateFactorY + coordinateOffsetY);
                if (elem.classList.contains("dot")) {
                    let pos = elem.id.split('-')
                    placeTokenOnBoard(pos[1], pos[2])
                }
            } else if (gamedata.state === 'MILL') {
                let mouse = d3.mouse(this);
                let elem = document.elementFromPoint(mouse[0] * coordinateFactorX + coordinateOffsetX, mouse[1] * coordinateFactorY + coordinateOffsetY);
                if (elem.classList.contains("player") && !elem.classList.contains(player)) {
                    removeTokenFromBoard(elem.id.split('-')[1], elem.id)
                }
            }
        }
    }
})

function addStone(playername, pos_x, pos_y) {
    let pos = document.getElementById('pos-' + pos_x + '-' + pos_y)
    if (playername === player) {
        let token = svg.append("circle")
            .attr('id', `${playername}-${d3.selectAll('circle.' + playername)._groups['0'].length}`)
            .attr('class', `player draggable ${playername}`)
            .attr("cx", pos.getAttribute('cx'))
            .attr("cy", pos.getAttribute('cy'))
            .attr("r", 30)
        dragHandler(token);
    } else {
        svg.append("circle")
            .attr('id', `${playername}-${d3.selectAll('circle.' + playername)._groups['0'].length}`)
            .attr('class', `player ${playername}`)
            .attr("cx", pos.getAttribute('cx'))
            .attr("cy", pos.getAttribute('cy'))
            .attr("r", 30)
    }
}

function removeStone(tokenid) {
    d3.select('circle#' + tokenid).remove()
}

let dragHandler = d3.drag()
    .on('drag', dragged)
    .on('start', dragstarted)
    .on('end', dragended);

let startposition = [];
let current;

function dragstarted() {

    setFactorOffset()
    if (gamedata.state === 'PLAYING_PHASE') {
        current = d3.select(this);
        current.style('cursor', 'grabbing')
        current.raise()
        startposition[0] = current.attr("cx")
        startposition[1] = current.attr("cy")
    }
}

function dragged() {

    setFactorOffset()
    if (gamedata.state === 'PLAYING_PHASE') {
        current = d3.select(this);
        current
            .attr('cx', d3.event.x)
            .attr('cy', d3.event.y);
    }
}

function dragended() {

    setFactorOffset()
    if (gamedata.state === 'PLAYING_PHASE') {
        hideStone(true)
        current.style('cursor', 'grab')
        let mouse = d3.mouse(this);
        let elem = document.elementFromPoint(mouse[0] * coordinateFactorX + coordinateOffsetX, mouse[1] * coordinateFactorY + coordinateOffsetY);
        hideStone(false)


        if (elem.classList.contains("dot")) {
            let pos = elem.id.split('-')
            moveToken(current.attr('id'), pos[1], pos[2])
            current
                .attr('cx', startposition[0])
                .attr('cy', startposition[1]);
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

function startGame() {
    var waitingpopup = document.getElementById("waitingpopup");
    waitingpopup.style.display = "none";

    let enemyName = document.getElementById('enemyName')
    if (gamedata.player1 === username) {
        player = 'player1'
        enemyplayer = 'player2'
        enemyName.innerText = gamedata.player2
    } else {
        player = 'player2'
        enemyplayer = 'player1'
        enemyName.innerText = gamedata.player1
    }

    nextMove()
}


function nextMove() {
    let dots = d3.selectAll('circle.dot')
    let ownTokens = d3.selectAll('circle.player1')
    let enemyTokens = d3.selectAll('circle.player2')
    let gamephase = document.getElementById('gamephase')
    if (gamedata.activePlayer === username) {
        ownTokens = d3.selectAll('circle.' + player)
        enemyTokens = d3.selectAll('circle.' + enemyplayer)
        switch (gamedata.state) {
            case 'PLACE_PHASE':
                gamephase.innerText = 'Platzieren Sie einen Spielstein auf einem freien Punkt.'
                dots.style('cursor', 'pointer')
                ownTokens.style('cursor', 'not-allowed')
                enemyTokens.style('cursor', 'not-allowed')
                break;
            case 'PLAYING_PHASE':
                gamephase.innerText = 'Bewegen Sie einen Spielsteine durch Drag&Drop.'
                dots.style('cursor', 'not-allowed')
                ownTokens.style('cursor', 'grab')
                enemyTokens.style('cursor', 'not-allowed')
                break;
            case 'MILL':
                gamephase.innerText = 'Entfernen Sie einen Spielstein Ihres Gegenspielers.'
                dots.style('cursor', 'not-allowed')
                ownTokens.style('cursor', 'not-allowed')
                enemyTokens.style('cursor', 'pointer')
                break;
            case'END':
                gamephase.innerText = 'Das Spiel ist beendet.'
                dots.style('cursor', 'default')
                ownTokens.style('cursor', 'default')
                enemyTokens.style('cursor', 'default')
                break;
            default:
                break;
        }
    } else {
        gamephase.innerText = 'Ihr Gegenspieler ist am Zug.'
        dots.style('cursor', 'not-allowed')
        ownTokens.style('cursor', 'not-allowed')
        enemyTokens.style('cursor', 'not-allowed')
    }

    if (gamedata.state === 'END') {
        if (gamedata.winner) {
            window.alert(gamedata.winner + ' hat gewonnen!')
        } else {
            window.alert('Unendschieden')
        }


        socket.emit('leave', {'room': gameid})


    }


    // let enemyName = document.getElementById('enemyName')
    // let ownName = document.getElementById('ownName')
    // let border = document.getElementById('border')
    // if (gamedata.activePlayer === username) {
    //     // border.style.stroke = 'var(--secondary-color)'
    //     // ownName.style.color = 'var(--secondary-color)'
    //     // enemyName.style.color = 'var(--secondary-color)'
    // } else {
    //     // border.style.stroke = 'var(--primary-color)'
    //     // ownName.style.color = 'var(--primary-color)'
    //     // enemyName.style.color = 'var(--primary-color)'
    // }
}


let gameid = false;
let gameUrl = document.getElementById("gameUrl")
if (gameUrl) {
    gameUrl.value = window.location.href
    gameid = window.location.href.split('/')[4]

    gameUrl.onclick = function copyUrl() {
        gameUrl.select();
        gameUrl.setSelectionRange(0, 99999);
        document.execCommand("copy");
    }
}
let username;
let gamedata;

/**
 * SOCKET
 */

let socket = io();
if (gameid) {
    socket.on('connect', function () {
        socket.emit('connected', {data: 'I\'m connected!'});

        socket.emit('join', {'gameid': gameid})
    });
}


/**
 * DEFAULT
 */
socket.on('message', function (data) {
})
socket.on('json', function (json) {
})
/**
 * get username
 */
socket.on('username', function (data) {
    username = data
})
/**
 * startGame
 */
socket.on('startGame', function (data) {
    gamedata = data;
    console.log(getGame())
    if (getGame() === 0) {
        socket.emit('syncGame', {
            'gameid': gameid
        })
    }
    console.log('startgame')
    startGame()
})
/**
 * Placing
 */
socket.on('tokenPlaced', function (data) {
    gamedata = data
    addStone(data.player, data.pos_x, data.pos_y)
    nextMove()
})

socket.on('ErrorPlacing', function (data) {
    gamedata = data
})

function placeTokenOnBoard(pos_x, pos_y) {
    socket.emit('placeTokenOnBoard', {
        'gameid': gameid,
        'player': player,
        'token': d3.selectAll('circle.' + player)._groups['0'].length,
        'pos_x': pos_x,
        'pos_y': pos_y
    })
}

/**
 * Moving
 */
socket.on('tokenMoved', function (data) {
    gamedata = data
    moveStone(data.player, data.tokenid, data.pos_x, data.pos_y)
    nextMove()
})
socket.on('ErrorMoving', function (data) {
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

/**
 * Removing
 */
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
    removeStone(data.tokenid)
    nextMove()
})

/**
 * Sync game on reload
 */
socket.on('syncGame', function (data) {
    console.log(data)
    if (getGame() === 0) {
        setGame(data.board)
    }
})

function getGame() {
    let tokens = d3.selectAll('circle.player')._groups['0']
    return tokens.length
}


function setGame(board) {

    let positions = d3.selectAll('circle.dot')._groups['0']
    let p = player === 'player1' ? 'P1' : 'P2'

    for (let i = 0; i < board.length; i++) {
        if (board[i] !== 'X') {
            tokeninfo = board[i].split('_')
            if (tokeninfo[0] === p) {
                let token = svg.append("circle")
                    .attr('id', player + '-' + tokeninfo[1])
                    .attr('class', `player draggable ${player}`)
                    .attr("cx", positions[i].attributes.cx.value)
                    .attr("cy", positions[i].attributes.cy.value)
                dragHandler(token);
            } else {
                svg.append("circle")
                    .attr('id', enemyplayer + '-' + tokeninfo[1])
                    .attr('class', `player ${enemyplayer}`)
                    .attr("cx", positions[i].attributes.cx.value)
                    .attr("cy", positions[i].attributes.cy.value)
            }
        }
    }
    nextMove()
}


// Get the popup
let popup = document.getElementById('popup');
let waitingpopup = document.getElementById('waitingpopup');

// When the user clicks anywhere outside of the popup, close it
window.onclick = function (event) {
    if (event.target === popup) {
        popup.style.display = "none";
    }
    if (event.target === waitingpopup) {
        waitingpopup.style.display = "none";
    }
}

function closePopup() {
    if (popup) {
        popup.style.display = "none";
    }
    if (waitingpopup) {

        waitingpopup.style.display = "none";
    }
}