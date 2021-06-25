/**
 * Author: Lorenz Adomat
 */
let sidebarState = 0

function expandSidebar() {
    if (window.matchMedia("(pointer: coarse)").matches) {
        if (sidebarState === 0) {
            document.getElementById('sidebar').style.display = 'flex'
            document.getElementById('main_block').style.display = 'none'
            document.getElementById('sidebar_icon').classList.remove('fa-bars')
            document.getElementById('sidebar_icon').classList.add('fa-times')
            sidebarState = 1
        } else {
            document.getElementById('sidebar').style.display = 'none'
            document.getElementById('main_block').style.display = 'block'
            document.getElementById('sidebar_icon').classList.remove('fa-times')
            document.getElementById('sidebar_icon').classList.add('fa-bars')
            sidebarState = 0
        }
    }
}