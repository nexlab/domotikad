#!/bin/bash 
mydir=`dirname $0`
cd $mydir
# java -jar ../compiler.jar --js $i --js_output_file $i.compressed
YUI="/usr/bin/yui-compressor"

CSS="../../resources/bootstrap/css/bootstrap.min.css
../../resources/glyphicons/css/bootstrap-glyphicons.css
../../resources/full-glyphicons/css/glyphicons.css
../../resources/bootstrap-switch/static/stylesheets/bootstrap-switch.css
../../resources/js/jqplot/jquery.jqplot.min.css
css/style.css
"

JS="
../../resources/js/jquery-1.10.2.min.js
../../resources/jquery-color/jquery.color.js
../../resources/hammer.js/hammer.js
../../resources/hammer.js/plugins/hammer.fakemultitouch.js
js/starthammer.js
../../resources/hammer.js/plugins/jquery.hammer.js/jquery.hammer.js
../../resources/bootstrap/js/bootstrap.min.js
../../resources/js/respond.min.js
../../resources/bootstrap-switch/static/js/bootstrap-switch.min.js
../../resources/Snap.js/snap.min.js
../../resources/AppScroll.js/AppScroll.min.js
../../resources/EventSource/eventsource.js
../../resources/js/jquery.easing.1.3.min.js
../../resources/js/jquery.alterclass.js
../../resources/js/jqplot/jquery.jqplot.min.js
../../resources/js/jqplot/plugins/jqplot.dateAxisRenderer.min.js
../../resources/js/jqplot/plugins/jqplot.highlighter.min.js
../../resources/js/jqplot/plugins/jqplot.cursor.min.js
../../resources/js/jqplot/plugins/jqplot.canvasTextRenderer.min.js
../../resources/js/jqplot/plugins/jqplot.canvasAxisTickRenderer.min.js
js/fastclick.js
js/speech.js
js/domotika.js
"
echo -n > css/combined.min.css
echo -n > js/combined.min.js
export IFS="
"
for c in $CSS
   do
      o=`basename $c`
      echo compressing $c ...
      rm -f /tmp/$o.compressed
      if [[ "$c" != *min.css ]] ; then
         $YUI --type css --nomunge -o /tmp/$o.compressed $c >/dev/null 2>&1
      else
         echo "already minified..."
         cp $c /tmp/$o.compressed
      fi
      cat /tmp/$o.compressed >> css/combined.min.css
   done

for j in $JS
   do
      echo compressing $j
      o=`basename $j`
      rm -f /tmp/$o.compressed
      if [[ "$j" != *min.js ]] ; then
         #java -jar ../../../tools/compiler.jar --js $mydir/$j --js_output_file /tmp/$o.compressed >/dev/null 2>&1
         $YUI --type js --nomunge -o /tmp/$o.compressed $j >/dev/null 2>&1
         if [ -f /tmp/$o.compressed ] ; then
            cat /tmp/$o.compressed >> js/combined.min.js
         else
            echo "cannot use closure, use htmlcompressor..."
            #sed -e 's/ \/\/.*$//' $mydir/$j  > /tmp/$o.pass1
            #java -jar ../../../tools/htmlcompressor-1.5.3.jar --nomunge -o /tmp/$o.compressed /tmp/$o.pass1
            cp $mydir/$j /tmp/$o.compressed
            cat /tmp/$o.compressed >> js/combined.min.js
         fi
      else
         echo "already minified..."
         cat $j >> js/combined.min.js
      fi
   done
   

