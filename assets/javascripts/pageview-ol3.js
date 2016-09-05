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
 *todo: Annotations

 */

define(["jquery", "ol3"], function($, ol) {    
    ol3 = ol;
    var hover;
    var barLayer
    var olpage;

    //Query the server for the bar boxes in a GeoJSON format
    initBarLayer = function() {
        var vectorSource = new ol.source.Vector({
            url: pageimage.regionURL,
            format: new ol.format.GeoJSON()
        });
        //All bar boxes drawn invisible by default
        var vectorLayer = new ol.layer.Vector({
            source: vectorSource,
            style:new ol.style.Style({
                        stroke: new ol.style.Stroke({
                            color: 'rgba(0,0,0,0)',
                            width: 1
                        })
                    })
            
        });         

        return vectorLayer;
    }

    //A hover interaction ol.interaction.Select
    //This makes the bar box visible on hover and position bar number
    //Clickthrough in JQuery uses this select's selected features
    initInteractions = function() {

        hover = new ol.interaction.Select({
            addCondition: ol.events.condition.click,
            condition: ol.events.condition.pointerMove,
            layers: [barLayer],
            style: function(feature, resolution) {
                if (resolution < 10) {
                    //Show numbers
                    if (resolution > 5) {
                        //Too small, show centred
                        var offsetX = 0;
                        var offsetY = 0;
                    } else {
                        //Move number to top left so it doesn't obscure bar
                        var width = feature.getGeometry().getExtent()[2] - feature.getGeometry().getExtent()[0];
                        var factor = 1 / resolution;
                        var paddingX = 25;
                        var paddingY = 30;
                        var offsetX = Math.round((width * factor) / 2) * -1 + (paddingX * factor);
                        var height = feature.getGeometry().getExtent()[3] - feature.getGeometry().getExtent()[1];
                        var offsetY = Math.round((height * factor) / 2) * -1 + (paddingY * factor);
                        
                    }

                    var style = new ol.style.Style({
                        stroke: new ol.style.Stroke({
                            color: 'red',
                            width: 1
                        }),
                        text: new ol.style.Text({
                            font: '18px Courier New, monospace',
                            text: feature.get('label'),
                            offsetX: offsetX,
                            offsetY: offsetY,
                            textAlign: 'center',
                            fill: new ol.style.Fill({
                                color: 'red'
                            }),
                            stroke: new ol.style.Stroke({
                                color: 'red',
                                width: 1
                            })
                        })
                    });

                } else {
                    //Don't show numbers, resolution too small
                    var style = new ol.style.Style({
                        stroke: new ol.style.Stroke({
                            color: 'red',
                            width: 1
                        })
                    });


                }
                return style   
            }            
        });


        return hover
    }

    //Load the map(page of music)
    initMap = function() {
        var url = pageimage.zoomify_url;
        var crossOrigin = 'anonymous';

        var imgWidth = pageimage.zoomify_width;
        var imgHeight = pageimage.zoomify_height;      

        //Set div width/height as proprortion of available screen
        var sf = imgHeight / imgWidth;
        var docWidth = parseInt($('body').width());
        var docHeight = parseInt($(window).height());
        var fullWidth = parseInt($('#pageimage').width());
        var fullHeight = fullWidth * sf;

        $("#map").css('width', fullWidth + "px").css("height", fullHeight + "px");
        console.log(fullWidth+'::'+fullHeight);

        var imgCenter = [imgWidth / 2, -imgHeight / 4];

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
        barLayer = initBarLayer();
        var interactions = initInteractions();
        olpage = new ol.Map({
            controls: ol.control.defaults({
                attributionOptions: /** @type {olx.control.AttributionOptions} */ ({
                    collapsible: false
                })
            }),

            layers: [
                new ol.layer.Tile({
                    source: pageimagesource
                }), barLayer
            ],

            target: 'map',
            view: new ol.View({
                projection: proj,
                center: imgCenter,
                zoom: 2
            })
        });
        olpage.addControl(new ol.control.ZoomSlider());
        //For debug only
        //olpage.addControl(new ol.control.MousePosition());
        olpage.addInteraction(interactions);

        //Extra click event for clickthrough to bars
        jQuery('#map').click(function(){
            var features = hover.getFeatures().getArray();
            if (features.length > 0){
                var feature=features[0];
                console.log(feature.get('label'));
                window.location = '/ocve/browse/barview?workid=' + pageimage.workid + '&pageimageid=' + pageimage.pageID + '&barid=' + feature.get("barid");
            }
        });      
        return olpage;
    }



    return initMap(ol);
});
