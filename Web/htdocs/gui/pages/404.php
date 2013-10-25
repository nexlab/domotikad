<canvas id="canvas" width="600" height="400" style="background-color: #000">
            FernetJS Invaders 404 - Not Found
           </canvas>
<script src="/resources/invaders404/invaders404.min.js"></script>
<script>
var invaders = new Invaders404({
    onLoose: function(){
        alert('You Loose!');
    },
    onWin: function(){
        alert('You Win!');
    }
});
invaders.start();
</script>
