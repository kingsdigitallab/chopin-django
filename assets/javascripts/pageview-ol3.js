/********
 *
 * Chopin project single page vew
 * Openlayers 3 version
 * Elliott Hall 15/2/2016
 *
 * This script uses the openlayers 3 library to display a single jp2 page of music, with a vector layer representing the bar boxes
 * drawn on top.  Boxes are clickable to link to single bar view.
 * Used in OCVE part of Chopin only.
 *
 */

define(["jquery", "ol3"], function ($, ol) {

    //Load the map(page of music)
    initMap = function (ol) {
        var imgWidth = pageimage.zoomify_width;
        var imgHeight = pageimage.zoomify_height;
        var url = pageimage.zoomify_url;
        console.log(url);
        var crossOrigin = 'anonymous';

        var imgCenter = [imgWidth / 2, -imgHeight/2];

        var proj = new ol.proj.Projection({
            code: 'ZOOMIFY',
            units: 'pixels',
            extent: [0, 0, imgWidth, imgHeight]
        });

        var source = new ol.source.Zoomify({
            url: url,
            size: [imgWidth, imgHeight],
            crossOrigin: crossOrigin
        });

        var map = new ol.Map({
            controls: ol.control.defaults({
                attributionOptions: /** @type {olx.control.AttributionOptions} */ ({
                    collapsible: false
                })
            }).extend([
                scaleLineControl
            ]),
            layers: [
                new ol.layer.Tile({
                    source: source
                })
            ],

            target: 'map',
            view: new ol.View({
                projection: proj,
                center: imgCenter,
                zoom: 2
            })
        });

    }
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
