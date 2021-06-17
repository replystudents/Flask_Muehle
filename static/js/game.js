/**
 * Set Offset and Factor for mouse functionality in the svg
 */
let coordinateOffsetX, coordinateOffsetY, coordinateFactorX, coordinateFactorY

function setFactorOffset() {
    coordinateOffsetX = document.getElementById("game").getBoundingClientRect().x
    coordinateOffsetY = document.getElementById("game").getBoundingClientRect().y
    coordinateFactorX = document.getElementById("game").getBoundingClientRect().width / svg.attr('viewBox').split(' ')[3]
    coordinateFactorY = document.getElementById("game").getBoundingClientRect().height / svg.attr('viewBox').split(' ')[2]
}

let gameid = false, gameUrl = document.getElementById("gameUrl")
/**
 * get gameid from url
 * set onclick event for copying the url to invite player
 */
if (gameUrl) {
    gameUrl.value = window.location.href
    gameid = window.location.href.split('/')[4]

    gameUrl.onclick = function copyUrl() {
        gameUrl.select()
        gameUrl.setSelectionRange(0, 99999)
        document.execCommand("copy")
    }
}

/**
 * Leave the SocketIO room when closing the game
 */
window.addEventListener('beforeunload', () => {
    socket.emit('leave', {'room': gameid})
})

let socket = io()
/**
 * Connect to SocketIO
 */
socket.on('connect', function () {
    socket.emit('connected', {data: 'I\'m connected!'})
    if (gameid) {
        socket.emit('join', {'gameid': gameid})
    }
})

let username
/**
 * socket: get username
 */
socket.on('username', function (data) {
    username = data
})

let svg = d3.select("svg#game")
/**
 * onclick event for placing and removing stones
 */
svg.on('click', function () {
    setFactorOffset()
    if (gamedata) {
        if (gamedata.activePlayer === username) {
            if (gamedata.state === 'PLACE_PHASE') {
                let mouse = d3.mouse(this)
                let elem = document.elementFromPoint(mouse[0] * coordinateFactorX + coordinateOffsetX, mouse[1] * coordinateFactorY + coordinateOffsetY)
                if (elem.classList.contains("dot")) {
                    let pos = elem.id.split('-')
                    placeTokenOnBoard(pos[1], pos[2])
                }
            } else if (gamedata.state === 'MILL') {
                let mouse = d3.mouse(this)
                let elem = document.elementFromPoint(mouse[0] * coordinateFactorX + coordinateOffsetX, mouse[1] * coordinateFactorY + coordinateOffsetY)
                if (elem.classList.contains("player") && !elem.classList.contains(player)) {
                    removeTokenFromBoard(elem.id.split('-')[1], elem.id)
                }
            }
        }
    }
})

/**
 * send place token request to server
 * @param pos_x
 * @param pos_y
 */
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
 * socket: place token validated by server
 */
socket.on('tokenPlaced', function (data) {
    gamedata = data
    addStone(data.player, data.pos_x, data.pos_y)
    nextMove()
})

/**
 * add stone
 * @param playername
 * @param pos_x
 * @param pos_y
 */
function addStone(playername, pos_x, pos_y) {
    let pos = document.getElementById('pos-' + pos_x + '-' + pos_y)
    if (playername === player) {
        let token = svg.append("circle")
            .attr('id', `${playername}-${d3.selectAll('circle.' + playername)._groups['0'].length}`)
            .attr('class', `player draggable ${playername}`)
            .attr("cx", pos.getAttribute('cx'))
            .attr("cy", pos.getAttribute('cy'))
            .attr("r", 30)
        dragHandler(token)
    } else {
        svg.append("circle")
            .attr('id', `${playername}-${d3.selectAll('circle.' + playername)._groups['0'].length}`)
            .attr('class', `player ${playername}`)
            .attr("cx", pos.getAttribute('cx'))
            .attr("cy", pos.getAttribute('cy'))
            .attr("r", 30)
    }
}

/**
 * send remove token request to server
 * @param token
 * @param tokenid
 */
function removeTokenFromBoard(token, tokenid) {
    socket.emit('removeToken', {
        'gameid': gameid,
        'player': player,
        'token': token,
        'tokenid': tokenid
    })
}

/**
 * socket: move token validated by server
 */
socket.on('tokenMoved', function (data) {
    gamedata = data
    moveStone(data.player, data.tokenid, data.pos_x, data.pos_y)
    nextMove()
})

/**
 * socket: remove token validated by server
 */
socket.on('tokenRemoved', function (data) {
    gamedata = data
    removeStone(data.tokenid)
    nextMove()
})

/**
 * remove stone
 * @param tokenid
 */
function removeStone(tokenid) {
    d3.select('circle#' + tokenid).remove()
}

/**
 * drag events for stones
 * @type {drag|*}
 */
let dragHandler = d3.drag()
    .on('drag', dragged)
    .on('start', dragstarted)
    .on('end', dragended)

let startposition = [], current

/**
 * start dragging stone
 * save starting position
 */
function dragstarted() {
    setFactorOffset()
    if (gamedata.state === 'PLAYING_PHASE') {
        current = d3.select(this)
        current.style('cursor', 'grabbing')
        current.raise()
        startposition[0] = current.attr("cx")
        startposition[1] = current.attr("cy")
    }
}

/**
 * dragging stone
 * set position of stone on mouse
 */
function dragged() {
    setFactorOffset()
    if (gamedata.state === 'PLAYING_PHASE') {
        current = d3.select(this)
        current
            .attr('cx', d3.event.x)
            .attr('cy', d3.event.y)
    }
}

/**
 * end dragging stone
 * send move to server
 */
function dragended() {
    setFactorOffset()
    if (gamedata.state === 'PLAYING_PHASE') {
        hideStone(true)
        current.style('cursor', 'grab')
        let mouse = d3.mouse(this)
        let elem = document.elementFromPoint(mouse[0] * coordinateFactorX + coordinateOffsetX, mouse[1] * coordinateFactorY + coordinateOffsetY)
        hideStone(false)
        if (elem.classList.contains("dot")) {
            let pos = elem.id.split('-')
            moveToken(current.attr('id'), pos[1], pos[2])
            current
                .attr('cx', startposition[0])
                .attr('cy', startposition[1])
        } else {
            current
                .attr('cx', startposition[0])
                .attr('cy', startposition[1])
        }

    }
}

/**
 * hide and unhide stone to check the element behind it
 * @param hide
 */
function hideStone(hide) {
    if (hide) {
        current.attr('style', 'display:none;')
    } else {
        current.attr('style', 'display:inline;')
    }
}

/**
 * send move token request to server
 * @param token
 * @param pos_x
 * @param pos_y
 */
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
 * move stone to new position
 * @param playername
 * @param tokenid
 * @param pos_x
 * @param pos_y
 */
function moveStone(playername, tokenid, pos_x, pos_y) {
    let token = d3.select('circle#' + tokenid)
    let dot = d3.select('circle#pos-' + pos_x + '-' + pos_y)
    token
        .attr('cx', dot.attr('cx'))
        .attr('cy', dot.attr('cy'))
}

let gamedata
/**
 * socket: start game
 */
socket.on('startGame', function (data) {
    gamedata = data
    if (getGame() === 0) {
        socket.emit('syncGame', {
            'gameid': gameid
        })
    }
    startGame()
})

let player, enemyplayer

/**
 * prepare game page on game start
 */
function startGame() {
    let waitingpopup = document.getElementById("waitingpopup")
    if (waitingpopup) {
        waitingpopup.style.display = "none"
    }

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

    if (gamedata.player1 === 'Bot' || gamedata.player2 === 'Bot') {
        let tieBtn = document.getElementById('tieBtn')
        tieBtn.style.display = 'none'
    }
    nextMove()
}

/**
 * adapt game page to game state
 */
function nextMove() {
    let dots = d3.selectAll('circle.dot')
    let ownTokens = d3.selectAll('circle.player1')
    let enemyTokens = d3.selectAll('circle.player2')
    let gamephase = document.getElementById('gamephase')
    let errormessage = document.getElementById('errormessage')
    errormessage.innerText = ''
    if (gamedata.activePlayer === username) {
        ownTokens = d3.selectAll('circle.' + player)
        enemyTokens = d3.selectAll('circle.' + enemyplayer)
        switch (gamedata.state) {
            case 'PLACE_PHASE':
                gamephase.innerText = 'Platzieren Sie einen Spielstein auf einem freien Punkt.'
                dots.style('cursor', 'pointer')
                ownTokens.style('cursor', 'not-allowed')
                enemyTokens.style('cursor', 'not-allowed')
                break
            case 'PLAYING_PHASE':
                gamephase.innerText = 'Bewegen Sie einen Spielsteine durch Drag&Drop.'
                dots.style('cursor', 'not-allowed')
                ownTokens.style('cursor', 'grab')
                enemyTokens.style('cursor', 'not-allowed')
                break
            case 'MILL':
                gamephase.innerText = 'Entfernen Sie einen Spielstein Ihres Gegenspielers.'
                dots.style('cursor', 'not-allowed')
                ownTokens.style('cursor', 'not-allowed')
                enemyTokens.style('cursor', 'pointer')
                break
            case'END':
                gamephase.innerText = 'Das Spiel ist beendet.'
                dots.style('cursor', 'default')
                ownTokens.style('cursor', 'default')
                enemyTokens.style('cursor', 'default')
                break
            default:
                break
        }
    } else {
        gamephase.innerText = 'Ihr Gegenspieler ist am Zug.'
        dots.style('cursor', 'not-allowed')
        ownTokens.style('cursor', 'not-allowed')
        enemyTokens.style('cursor', 'not-allowed')
    }

    if (gamedata.state === 'END') {
        let tieBtn = document.getElementById('tieBtn')
        let surrenderBtn = document.getElementById('surrenderBtn')
        tieBtn.disabled = true
        surrenderBtn.disabled = true

        let endpopuptext = document.getElementById('endpopuptext')
        if (gamedata.winner) {
            gamephase.innerHTML = 'Das Spiel ist beendet.' + '<br>' + gamedata.winner + ' hat gewonnen!'
            endpopuptext.innerText = gamedata.winner + ' hat gewonnen!'
        } else {
            gamephase.innerHTML = 'Das Spiel ist beendet.' + '<br>' + 'Das Ergebnis ist ein Unentschieden.'
            endpopuptext.innerText = 'Unentschieden'
        }
        endpopup.style.display = "block"

        socket.emit('leave', {'room': gameid})
    }
}

/**
 * socket: error when trying to place a stone
 */
socket.on('ErrorPlacing', function (data) {
    gamedata = data
    let errormessage = document.getElementById('errormessage')
    errormessage.innerText = 'Diese Position ist ungültig.'
})
/**
 * socket: error when trying to move a stone
 */
socket.on('ErrorMoving', function (data) {
    gamedata = data
    let errormessage = document.getElementById('errormessage')
    errormessage.innerText = 'Der Spielstein kann nicht an diese Position bewegt werden.'
})
/**
 * socket: error when trying to remove a stone
 */
socket.on('ErrorRemoving', function (data) {
    gamedata = data
    let errormessage = document.getElementById('errormessage')
    errormessage.innerText = 'Dieser Spielstein kann nicht entfernt werden.'
})

/**
 * socket: syncing the game
 */
socket.on('syncGame', function (data) {
    if (getGame() === 0) {
        setGame(data.board)
    }
})

/**
 * get the number of stones
 * @returns {*}
 */
function getGame() {
    let tokens = d3.selectAll('circle.player')._groups['0']
    return tokens.length
}

/**
 * place stones that were received after sync request
 * @param board
 */
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
                dragHandler(token)
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

/**
 * onclick function for tie button
 */
function tie() {
    if (gamedata) {
        let tieBtn = document.getElementById('tieBtn')
        socket.emit('tieGame', {
            'gameid': gameid
        })
        tieBtn.disabled = true
    }
}

/**
 * socket: tie game
 */
socket.on('wantsToTie', function () {
    let tieBtn = document.getElementById('tieBtn')
    tieBtn.classList.add('btn-outline-warning')
})

let surrenderCounter = 0

/**
 * onclick function for surrender button
 */
function surrender() {
    if (gamedata) {
        let surrenderBtn = document.getElementById('surrenderBtn')
        if (surrenderCounter === 0) {
            surrenderBtn.classList.add('btn-outline-warning')
            surrenderCounter++
        } else if (surrenderCounter === 1) {
            surrenderBtn.classList.add('btn-outline-danger')
            surrenderCounter++

        } else {
            if (gamedata) {
                socket.emit('surrenderGame', {
                    'gameid': gameid,
                    'winner': gamedata[enemyplayer]
                })
                surrenderBtn.disabled = true
            }
        }
    }
}

/**
 * socket: update game state after tie or surrender
 */
socket.on('updateGameState', function (data) {
    gamedata = data
    nextMove()
})

/**
 * get popup elements
 */
let popup = document.getElementById('popup')
let waitingpopup = document.getElementById('waitingpopup')
let endpopup = document.getElementById('endpopup')

/**
 * close popups when clicking ouside of the popup
 * @param event
 */
window.onclick = function (event) {
    if (event.target === popup) {
        popup.style.display = "none"
    }
    if (event.target === waitingpopup) {
        waitingpopup.style.display = "none"
    }
    if (event.target === endpopup) {
        endpopup.style.display = "none"
    }
}

/**
 * onclick function for popup close button
 */
function closePopup() {
    if (popup) {
        popup.style.display = "none"
    }
    if (waitingpopup) {
        waitingpopup.style.display = "none"
    }
    if (endpopup) {
        endpopup.style.display = "none"
    }
}
