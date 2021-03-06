window.onload = function() {
  var basemap = L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution:
      '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
  });
  $.getJSON('../output/geo_data.json', function(data) {
    var geojson = L.geoJson(data, {
      onEachFeature: function(feature, layer) {
        layer.bindPopup(feature.properties.text);
      }
    });

    var map = L.map('map').fitBounds(geojson.getBounds());
    // .setView([0.0,-10.0], 2);
    basemap.addTo(map);
    geojson.addTo(map);
  });
};
