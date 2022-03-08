<html>
  <head>
   <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>

   <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
   <script type="text/javascript">
      google.charts.load('current', {'packages':['gauge']});
      google.charts.setOnLoadCallback(drawChart);

      function drawChart() {

        var data = google.visualization.arrayToDataTable([
          ['Label', 'Value'],
          ['Humedad', 0]
        ]);

        var options = {
          width: 400, height: 400,
          redFrom: 90, redTo: 100,
          yellowFrom:75, yellowTo: 90,
          minorTicks: 5
        };

        var chart = new google.visualization.Gauge(document.getElementById('chart_div'));

        chart.draw(data, options);

        setInterval(function() {
//################################################################################//
        $.ajax ({
               url: "http://192.168.1.46/consulhum.php",
               success: function(respuesta){
                    var obj = JSON.parse(respuesta);
                     hum = obj.hum;
                     console.log(hum);
                     data.setValue(0, 1,hum);
              },
              error: function(){
                     console.log("no se a podido la informacion")
           }
  });

//##############################################################################//
          chart.draw(data, options);
        }, 130);
      }
    </script>
  </head>
  <body>
    <div id="chart_div" style="width: 400px; height: 120px;"></div>
  </body>
</html>
