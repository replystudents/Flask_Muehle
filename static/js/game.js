/**
 let selectedElement, offset, transform;


 let game = document.getElementById('game')
 let body = d3.select('body')

 svg = body.append('svg').attr('width', 300).attr('height', 300)

 svg.append('circle').attr('cx', 130).attr('cy', 130).attr('r', 15).attr('class', 'draggable').call()


 d3.selectAll(".draggable").call(d3.drag().on("start", started));

 function started(event) {
    console.log("started")
    let circle = d3.select(this).classed("dragging", true);
    console.log(event)
    event.on("drag", dragged).on("end", ended);

    function dragged(event, d) {
        console.log(circle)
        circle.raise().attr("cx", d.x = event.x).attr("cy", d.y = event.y);
    }

    function ended() {
        circle.classed("dragging", false);
    }
}

 // https://github.com/d3/d3-drag

 function onDragDrop(dragHandler, dropHandler) {
    let drag = d3.drag();

    drag.on("drag", dragHandler)
        .on("dragend", dropHandler);
    return drag;
}

 let g = d3.select("body").select("svg").append("g")
 .data([{ x: 50, y: 50 }]);

 g.append("rect")
 .attr("width", 40)
 .attr("height", 40)
 .attr("stroke", "red")
 .attr("fill","transparent")
 .attr("x", function (d) { return d.x; })
 .attr("y", function (d) { return d.y; })
 .call(onDragDrop(dragmove, dropHandler));

 g.append("text")
 .text("Any Text")
 .attr("x", function (d) { return d.x; })
 .attr("y", function (d) { return d.y; })
 .call(onDragDrop(dragmove, dropHandler));

 function dropHandler(d) {
    // alert('dropped');
}

 function dragmove(d) {
    d3.select(this)
        .attr("x", d.x = d3.event.x)
        .attr("y", d.y = d3.event.y);
}

 */
console.log(document)
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

// console.log(coordinateFactorX, coordinateFactorY)

// svg.on('mousemove', function(){
//     let mouse = d3.mouse(this);
//     let elem = document.elementFromPoint((mouse[0])*coordinateFactorX, (mouse[1])*coordinateFactorY);
//     console.log(elem.id, "mouse", mouse)
// })

let players = {player1: [], player2: []}
let placingPhase = true;
let hasMuehle = true;

svg.on('click', function () {
    if (placingPhase === true) {
        if (players["player1"].length < 9 || players["player2"].length < 9) {
            let player = players["player2"].length < players["player1"].length ? 'player2' : 'player1';

            let mouse = d3.mouse(this);
            let elem = document.elementFromPoint(mouse[0] * coordinateFactorX + coordinateOffsetX, mouse[1] * coordinateFactorY + coordinateOffsetY);
            if (elem.classList.contains("dot")) {

                addStone(player)
            }
        } else {
            placingPhase = false;
        }
    } else {

        // if (hasMuehle === true) {
        //     let player = 'player1'
        //
        //     if (current.classList.contains(player)) {
        //         removeStone()
        //     }
        // }
    }


})

function addStone(player) {
    let stone = svg.append("circle")
        .attr('id', `${player}${players[player].length}`)
        .attr('class', `player draggable ${player}`)
        .attr("cx", Math.round(((d3.event.x - coordinateOffsetX) / coordinateFactorX) / 50) * 50)
        .attr("cy", Math.round(((d3.event.y - coordinateOffsetY) / coordinateFactorY) / 50) * 50)
        .attr("r", 30)
        .on('contextmenu', function () {
            d3.event.preventDefault()
            removeStone();
        });

    if (player === 'player1') {
        players["player1"].push(stone)
    } else {
        players["player2"].push(stone)
    }
    dragHandler(stone);
}

function removeStone() {
    current.remove()

}

let dragHandler = d3.drag()
    .on('drag', dragged)
    .on('start', dragstarted)
    .on('end', dragended);

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

let startposition = [];
let current;

function dragstarted() {
    current = d3.select(this);
    current.raise()
    startposition[0] = current.attr("cx")
    startposition[1] = current.attr("cy")
    //console.log("startposition", startposition)
}

function dragged() {
    current = d3.select(this);
    current
        .attr('cx', d3.event.x)
        .attr('cy', d3.event.y);
}

function dragended() {
    hideStone(true)
    let mouse = d3.mouse(this);
    let elem = document.elementFromPoint(mouse[0] * coordinateFactorX + coordinateOffsetX, mouse[1] * coordinateFactorY + coordinateOffsetY);
    //console.log(elem)
    //console.log("mouse",mouse)
    hideStone(false)
    if (elem.classList.contains("dot")) {
        current
            .attr('cx', Math.round(d3.event.x / 50) * 50)
            .attr('cy', Math.round(d3.event.y / 50) * 50);
    } else {
        current
            .attr('cx', startposition[0])
            .attr('cy', startposition[1]);
    }

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

// Get the modal
var modal = document.getElementById("popup");
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

function startGame() {
    console.log("start")
    modal.style.display = "none";
}

function startBotGame() {
    modal.style.display = "none";
}


let gameUrl = document.getElementById("gameUrl")
if (gameUrl) {
    gameUrl.value = window.location.href

    gameUrl.onclick = function copyUrl() {

    /* Select the text field */
    gameUrl.select();
    gameUrl.setSelectionRange(0, 99999); /* For mobile devices */

    /* Copy the text inside the text field */
    document.execCommand("copy");

    /* Alert the copied text */
    console.log("Copied the text: " + gameUrl.value);
}
}
