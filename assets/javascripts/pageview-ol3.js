/********
 *
 * Chopin project single page vew
 * ol 3 version
 * Elliott Hall 15/2/2016
 *
 * This script uses the ol 3 library to display a single jp2 page of music, with a vector layer representing the bar boxes
 * drawn on top.  Boxes are clickable to link to single bar view.
 * Used in OCVE part of Chopin only.
 *
 *
 * var barStyles = new ol.StyleMap({
        "default": new ol.Style({
            strokeOpacity: 0,
            fillOpacity: 0.0,
            labelAlign: labelAlign
        }),
        "barSelector": new ol.Style({
            strokeOpacity: 0,
            fillOpacity: 0.0
        }),
        "Initial": new ol.Style({
            strokeOpacity: 0,
            fillOpacity: 0.0,
            labelAlign: labelAlign
        }),
        "annotation": new ol.Style({
            strokeOpacity: 1,
            fillOpacity: 0.0,
            strokeColor: 'green',
            label: "${label}",
            labelAlign: labelAlign,
            labelOutlineColor: "white",
            labelOutlineWidth: 3,
            fontColor: "black",
            fontSize: fontSize,
            fontFamily: "Courier New, monospace",
            fontWeight: "bold"
        }),
        "select": new ol.Style({
            strokeOpacity: 1,
            strokeWidth: 1,
            fillColor: "${fillColor}",
            fillOpacity: 0.3,
            pointRadius: 6,
            pointerEvents: "visiblePainted",
            // label with \n linebreaks
            label: "${label}",
            fontColor: "black",
            fontSize: fontSize,
            fontFamily: "Courier New, monospace",
            fontWeight: "bold",
            labelAlign: labelAlign,
            labelOutlineColor: "white",
            labelOutlineWidth: 3
        }),
        "temporary": new ol.Style({
            strokeOpacity: 1,
            strokeWidth: 1,
            strokeColor: 'red',
            pointRadius: 6,
            pointerEvents: "visiblePainted",
            // label with \n linebreaks
            label: "${label}",
            labelAlign: labelAlign,
            labelOutlineColor: "white",
            labelOutlineWidth: 3,
            fontColor: "red",
            fontSize: "12px",
            fontFamily: "Courier New, monospace",
            fontWeight: "bold"
        })
    });
    style: styleFunction
 */

define(["jquery", "ol3"], function ($, ol) {
    var map;
ol3=ol;
    var fontSize = '12px';
    var labelAlign = 'cb';    


    //Query the server for the bar boxes in a GeoJSON format
    initBarLayer=function(){
      var vectorSource= new ol.source.Vector({
          url: pageimage.regionURL,
          format: new ol.format.GeoJSON()
        });

      var vectorLayer = new ol.layer.Vector({
        source: vectorSource,
        
      });

      return vectorLayer;
    }

    //Bar
    initInteractions=function(){
        var select = new ol.interaction.Select({
        wrapX: false
      });
        var modify = new ol.interaction.Modify({
        features: select.getFeatures()
      });

       return ol.interaction.defaults().extend([select, modify])
    }

    //Load the map(page of music)
    initMap = function () {
        var imgWidth = pageimage.zoomify_width;
        var imgHeight = pageimage.zoomify_height;
        var url = pageimage.zoomify_url;
        var scaleLineControl = new ol.control.ScaleLine();
        var crossOrigin = 'anonymous';

        var imgCenter = [imgWidth / 2, -imgHeight/4];

        var proj = new ol.proj.Projection({
            code: 'ZOOMIFY',
            units: 'pixels',
            extent: [0, 0, imgWidth, imgHeight]
        });

        var pageimagesource = new ol.source.Zoomify({
            url: url,
            size: [imgWidth, imgHeight],
            crossOrigin: crossOrigin
        });
        //Get the bar boxes
        barLayer=initBarLayer();
        interactions=initInteractions();
        olpage = new ol.Map({
            interactions: interactions,
            controls: ol.control.defaults({
                attributionOptions: /** @type {olx.control.AttributionOptions} */ ({
                    collapsible: false
                })
            }),

            layers: [
                new ol.layer.Tile({
                    source: pageimagesource
                })
                ,barLayer
            ],

            target: 'map',
            view: new ol.View({
                projection: proj,
                center: imgCenter,
                zoom: 2
            })
        });
        olpage.addControl(new ol.control.ZoomSlider());
        olpage.addControl(new ol.control.MousePosition());
        return olpage;
    }




	return initMap(ol);
});


//load the bar coordinates as an ol3 vector layer
initBarLayer = function () {

}

function onFeatureSelect(feature) {

}

function onFeatureUnselect(feature) {
}

function showBar(feature) {

}

function hideBar(feature) {

}
