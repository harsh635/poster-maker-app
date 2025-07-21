export default {
  mounted(el) {
    el.style.position = 'absolute'
    el.onmousedown = function (e) {
      const shiftX = e.clientX - el.getBoundingClientRect().left
      const shiftY = e.clientY - el.getBoundingClientRect().top

      function moveAt(pageX, pageY) {
        el.style.left = pageX - shiftX + 'px'
        el.style.top = pageY - shiftY + 'px'
      }

      function onMouseMove(e) {
        moveAt(e.pageX, e.pageY)
      }

      document.addEventListener('mousemove', onMouseMove)

      el.onmouseup = () => {
        document.removeEventListener('mousemove', onMouseMove)
        el.onmouseup = null
      }
    }

    el.ondragstart = () => false
  }
}
