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

 */

define(["jquery", "ol3"], function ($, ol) {
    ol3 = ol;
    var hover;
    var barLayer;
    var noteLayer;
    var olpage;
    var styles;
    var annotationInteraction;

    //The Open Layers bar styles
    // invisible: default setting for bar regions
    // hover: For displaying bar number and boundary on hover
    // visibleNote: Annotation
    // selectedNote: Annotation selected
    initStyles = function () {
        var invisibleStyle = new ol.style.Style({
            stroke: new ol.style.Stroke({
                color: 'rgba(0,0,0,0)',
                width: 1
            })
        });

        var hoverStyle = function (feature, resolution) {
            if (resolution < 10) {
                //Show numbers
                if (resolution > 4) {
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

        var visibleNoteStyle = new ol.style.Style({
            stroke: new ol.style.Stroke({
                color: 'yellow',
                width: 1
            })
        });

        var selectedNoteStyle = new ol.style.Style({
            stroke: new ol.style.Stroke({
                color: 'blue',
                width: 1
            })
        });

        styles = {invisible: invisibleStyle, hover: hoverStyle, visibleNote: visibleNoteStyle, selectedNote: selectedNoteStyle}
    }

    //Query the server for the bar boxes in a GeoJSON format
    initBarLayer = function () {
        var vectorSource = new ol.source.Vector({
            url: pageimage.regionURL,
            format: new ol.format.GeoJSON()
        });
        //All bar boxes drawn invisible by default
        var vectorLayer = new ol.layer.Vector({
            source: vectorSource,
            style: styles.invisible

        });

        return vectorLayer;
    }

    //A hover interaction ol.interaction.Select
    //This makes the bar box visible on hover and position bar number
    //Clickthrough in JQuery uses this select's selected features
    initInteractions = function () {

        hover = new ol.interaction.Select({
            addCondition: ol.events.condition.click,
            condition: ol.events.condition.pointerMove,
            layers: [barLayer],
            style: styles.hover
        });


        return hover
    }

    //Load the map(page of music)
    initMap = function () {
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

        //TODO Debug only remove


        initStyles();

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
        //Get any annotations
        //todo fix later when annotations done
        var showNotes = false;
        if (pageimage.annotation_mode == 1) {
            showNotes = true;
        }
        noteLayer = initAnnotationLayer(showNotes);
        olpage = new ol.Map({
            controls: ol.control.defaults({
                attributionOptions: /** @type {olx.control.AttributionOptions} */ ({
                    collapsible: false
                })
            }),

            layers: [
                new ol.layer.Tile({
                    source: pageimagesource
                }), barLayer, noteLayer
            ],

            target: 'map',
            view: new ol.View({
                projection: proj,
                center: imgCenter,
                zoom: 2
            })
        });
        console.log(fullWidth + '::' + fullHeight);
        olpage.addControl(new ol.control.ZoomSlider());
        //For debug only
        olpage.addControl(new ol.control.MousePosition());
        //Add interactions depending on mode
        var interactions = null;
        if (pageimage.annotation_mode == 0) {

            interactions = initInteractions();
            //Extra click event for clickthrough to bars
            jQuery('#map').click(function () {
                var features = hover.getFeatures().getArray();
                if (features.length > 0) {
                    var feature = features[0];
                    console.log(feature.get('label'));
                    window.location = '/ocve/browse/barview?workid=' + pageimage.workid + '&pageimageid=' + pageimage.pageID + '&barid=' + feature.get("barid");
                }
            });
            olpage.addInteraction(interactions);
        } else {
            //Links on right
            initAnnotationTriggers();
        }

        return olpage;
    }


    /* ************************************************************
     Annotation Functions
     Notes can be attached to three different shapes: a bar region, a drawn square and a drawn circle
     */


    initAnnotationLayer = function (visible) {
        var vectorSource = new ol.source.Vector({
            url: pageimage.noteURL,
            format: new ol.format.GeoJSON()
        });

        //All bar boxes drawn invisible by default
        return new ol.layer.Vector({
            source: vectorSource,
            style: styles.visibleNote,
            visible: visible
        });

    }

    initAnnotationTriggers = function () {
        //Bind annotation events to elements
        if ($(newNoteForm).length > 0) {

            //Annoation draw tools
            $(pageimage.barAttachToggle).click(function () {
                 initDrawInteraction("Bar");
            });

            $(newSquareNoteToggle).click(function () {
                initDrawInteraction("Polygon");
            });
            $(newCircleNoteToggle).click(function () {
                initDrawInteraction("Circle");
            });


            //Form triggers
            $('#cancelNote').click(function () {
                resetPage();
                return false;
            });

        }


    }

    endDrawInteraction = function () {
        //remove any existing interaction
        console.log(olpage.getInteractions().length);
        olpage.removeInteraction(annotationInteraction);

    }

    initDrawInteraction = function (noteType) {
        endDrawInteraction();
        //Create annotation
        var type;
        var drawOptions;
        if (noteType == "Polygon" || noteType == "Circle") {
            type = 'Circle';
            if (noteType == "Polygon") {
                //type = ol.geom.Polygon;
                var geometryFunction = ol.interaction.Draw.createRegularPolygon(4);
                drawOptions = {
                    type: (type),
                    layers: [noteLayer],
                    geometryFunction: geometryFunction

                }

            } else if (noteType == "Circle") {
                // type = ol.geom.Polygon;
                drawOptions = {
                    layers: [noteLayer],
                    type: (type)
                }
            }
            annotationInteraction = new ol.interaction.Draw(drawOptions);
            annotationInteraction.on('drawend', finishDraw);

        } else if (noteType == "Bar") {
            //todo: Actually a select, not draw
            annotationInteraction = initInteractions();
            jQuery('#map').click(function () {
                if (hover && hover.getFeatures().length > 0) {

                    var features = hover.getFeatures().getArray();
                    if (features.length > 0) {
                        var feature = features[0];
                        console.log(feature.get('label'));
                        finishDraw(feature);
                    }
                }
            });

        }
        //todo Check if form is visible, make visible if not
        console.log(annotationInteraction);
        olpage.addInteraction(annotationInteraction);

    }

    finishDraw = function (event) {
        var feature = event.feature
        var format = new ol.format.GeoJSON();
        console.log(format.writeFeature(feature));
        //Add shape id to note form
        $('#id_noteregions').val(format.writeFeature(feature));
        $('#featureid').val(feature.id);


    }

    attachDeleteNote = function (selector) {
        $(selector).click(function () {
            var sure = confirm('Delete This Note?');
            if (sure == true) {
                var noteid = $(this).data('noteid');
                $.post('/ocve/deleteNote/' + noteid, function (data) {
                    $('#comment-' + noteid).fadeOut();
                    $('#comment-' + noteid).next('hr').fadeOut();
                    $('#messages').html(data.messages);
                    noteFeatures = alayer.getFeaturesByAttribute('noteid', noteid);
                    alayer.removeFeatures(noteFeatures);
                    incrementNoteCount(-1);
                }, 'json');
            }
            return false;
        });
    }

    attachUpdateNote = function (selector) {
        $(selector).click(function () {
            var noteid = $(this).data('noteid');
            nTest = noteid;
            var oldText = $('#comment-' + noteid + ' div.annotation p').html();
            $('#id_notetext').val(oldText);
            $('#annotation_id').val(noteid);
            //Select current notes/regions
            curFeatures = alayer.getFeaturesByAttribute('noteid', noteid);
            for (var c = 0; c < curFeatures.length; c++) {

                curFeatures[c].renderIntent = 'visibleNote';
                noteSelectFeature.select(curFeatures[c]);
            }
            alayer.redraw();
            showNewAnnotationWindow();

        });
    }
    //Change the user annotation count by inc
    incrementNoteCount = function (inc) {
        var count = parseInt($('#note_count').html())
        count += inc;
        $('#note_count').html(count)
        if (count == 0) {
            //No more notes, hide dropdown
            $('#notes').hide();
        }
    }

    showNewAnnotationWindow = function () {
        if ($('#newNote').is(':visible') == false) {
            $('#newNote').fadeIn();
            $('#notes').hide();
            $('#commentary').hide()
        }
    };

    resetPage = function(){
        endDrawInteraction();
    }

    hideNewAnnotationWindow = function () {
        if ($('#newNote').is(':visible')){
            $('#newNote').fadeOut();
            $('#notes').show();
            $('#commentary').show();
        }
    };
    return initMap(ol);
});
