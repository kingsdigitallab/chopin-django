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
    var commentLayer;
    var olpage;
    var styles;
    var annotationInteraction;
    var noteSelectInteraction;
    var noteSource;

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
                color: '#ffcc33',
                width: 1
            }),
            image: new ol.style.Circle({
                radius: 7,
                fill: new ol.style.Fill({
                    color: '#ffcc33'
                })
            })
        });

        var visibleCommentStyle = new ol.style.Style({

            stroke: new ol.style.Stroke({
                color: 'red',
                width: 1
            }),
            image: new ol.style.Circle({
                radius: 7,
                fill: new ol.style.Fill({
                    color: '#ffcc33'
                })
            })
        });

        var selectedNoteStyle = new ol.style.Style({
            stroke: new ol.style.Stroke({
                color: 'blue',
                width: 1
            })
        });

        styles = {invisible: invisibleStyle, hover: hoverStyle, visibleComment: visibleCommentStyle, visibleNote: visibleNoteStyle, selectedNote: selectedNoteStyle}
    }

    //Query the server for the bar boxes in a GeoJSON format
    initBarLayer = function () {
        var vectorSource = new ol.source.Vector({
            url: pageimage.regionURL,
            format: new ol.format.GeoJSON()
        });
        var barStyle = styles.invisible;
        var visible = true;
        if (pageimage.annotation_mode) {
            barStyle = styles.hover;
            visible = false;
        }
        //All bar boxes drawn invisible by default
        var vectorLayer = new ol.layer.Vector({
            source: vectorSource,
            style: barStyle,
            visible: visible
        });

        return vectorLayer;
    }

    //A hover interaction ol.interaction.Select
    //This makes the bar box visible on hover and position bar number
    //Clickthrough in JQuery uses this select's selected features
    initInteractions = function () {

//        hover = new ol.interaction.Select({
//            addCondition: ol.events.condition.click,
//            condition: ol.events.condition.pointerMove,
//            layers: [barLayer],
//            style: styles.hover
//        });
        initModifyInteraction()

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


        initStyles();
        var cHeight = imgHeight / 2;

        var imgCenter = [imgWidth / 2, -cHeight];


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
        commentLayer = initCommentLayer(showNotes);
        olpage = new ol.Map({
            controls: ol.control.defaults({
                attributionOptions: /** @type {olx.control.AttributionOptions} */ ({
                    collapsible: false
                })
            }),

            layers: [
                new ol.layer.Tile({
                    source: pageimagesource
                }), barLayer, noteLayer, commentLayer
            ],

            target: 'map',
            view: new ol.View({
                projection: proj,
                center: imgCenter,
                zoom: 2
            })
        });
        //TODO Debug only remove
        //Set center
        var view = olpage.getView();
        var viewerFullHeight = olpage.getSize()[1] * view.getResolution();
        var viewerFullWidth = olpage.getSize()[0] * view.getResolution();
        var imageFullHeight = view.getProjection().getExtent()[3];
        var x = viewerFullWidth / 2;
        var y = -1 * (viewerFullHeight / 2);
        if (viewerFullHeight < imageFullHeight) {
            view.setCenter([x, y]);
        }

        olpage.addControl(new ol.control.ZoomSlider());
        //For debug only
        //olpage.addControl(new ol.control.MousePosition());
        //Add interactions depending on mode
        var interactions;
        if (pageimage.annotation_mode == 1) {
            interactions = initAnnotationInteractions();
            // Link notes in right sidebar to features
            jQuery('div.annotation').click(function (e) {
                var features = noteLayer.getSource().getFeatures().concat(commentLayer.getSource().getFeatures());
                if ($(this).data('noteid')) {
                    var noteid = $(this).data('noteid');
                    if (features.length > 0) {
                        for (var x = 0; x < features.length; x++) {
                            var feature = features[x];
                            if (noteid == feature.getProperties().noteid) {
                                noteSelectInteraction.getFeatures().clear();
                                noteSelectInteraction.getFeatures().push(feature);
                                $('.annotation-box').css('border', 'none');
                                $('#comment-' + noteid).css('border', '1px solid red');
                            }
                        }

                    }
                }

            });
        } else {
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
        }

        return olpage;
    }


    /* Annotation Functions
     Notes can be attached to three different shapes: a bar region, a drawn square and a drawn circle
     */


    initAnnotationLayer = function (visible) {
        noteSource = new ol.source.Vector({
            url: pageimage.noteURL,
            format: new ol.format.GeoJSON()
        });

        //All bar boxes drawn invisible by default
        //visible: visible
        return new ol.layer.Vector({
            source: noteSource,
            style: styles.visibleNote,
            visible: visible

        });

    }

    initCommentLayer = function (visible) {
        commentSource = new ol.source.Vector({
            url: pageimage.commentURL,
            format: new ol.format.GeoJSON()
        });

        //All bar boxes drawn invisible by default
        //visible: visible
        return new ol.layer.Vector({
            source: commentSource,
            style: styles.visibleComment,
            visible: visible

        });

    }

    initAnnotationInteractions = function () {
        //Bind annotation events to elements
        if ($(newNoteForm).length > 0) {
            $(pageimage.barAttachToggle).click(function () {
                initDrawInteraction("Bar");
            });

            $(newSquareNoteToggle).click(function () {
                initDrawInteraction("Polygon");
            });
            $(newCircleNoteToggle).click(function () {
                initDrawInteraction("Circle");
            });

            $('#newNoteForm').submit(function (event) {
                saveNote();
            });
            $('a.updateNote').click(function () {
                var noteid = $(this).data('noteid');
                nTest = noteid;
                var oldText = $('#comment-' + noteid + ' div.annotation p').html();
                $('#id_notetext').val(oldText);
                $('#annotation_id').val(noteid);
                var features = noteLayer.getSource().getFeatures();
                if (noteid) {
                    if (features.length > 0) {
                        for (var x = 0; x < features.length; x++) {
                            var feature = features[x];
                            if (noteid == feature.getProperties().noteid) {
                                noteSelectInteraction.getFeatures().clear();
                                noteSelectInteraction.getFeatures().push(feature);
                                $('.annotation-box').css('border', 'none');
                                $('#comment-' + noteid).css('border', '1px solid red');
                            }
                        }

                    } else {
                        console.log('Features not found for ' + noteid);
                    }
                } else {
                    console.log('noteid not found');
                }

            });

            $('#cancelNote').click(function (event) {
                event.preventDefault();
                endDrawInteraction();
                return false;
            });
        }
        //General esc capture to stop a draw interaction
        $(document).keyup(function (e) {
            if (e.keyCode === 27) {
                olpage.getInteractions().forEach(function (interaction) {
                    if (interaction == annotationInteraction) {
                        endDrawInteraction();
                    }
                });
            }
        });

        noteSelectInteraction = new ol.interaction.Select({
            condition: ol.events.condition.click
        });
        olpage.addInteraction(noteSelectInteraction);

        noteSelectInteraction.on('select', function (e) {
            var feature = e.selected[0];
            var noteid = feature.getProperties().noteid;
            $('.annotation-box').css('border', 'none');
            $('#comment-' + noteid).css('border', '1px solid red');
            if (!$('#comment-' + noteid).is(':visible')) {
                if ($('#comment-' + noteid).attr('class').includes('commentary')) {
                    $('#commentary h4').click();
                } else {
                    $('#notes h4').click();
                }
            }
            // console.log(feature.getProperties().noteid );
        });
    }

    endDrawInteraction = function () {
        //remove any existing interaction
        olpage.removeInteraction(annotationInteraction);
        olpage.addInteraction(noteSelectInteraction);
    }


    /**
     * Based on Geoffroy's modify interaction from Digipal
     *
     * https://github.com/kcl-ddh/digipal/blob/master/digipal_text/static/digipal_text/viewer/annotation.ts
     */

    var Modify = (function (_super) {
    __extends(Modify, _super);
    //nearestVertexCoordinates_: ;
    function Modify(options, vectorLayer, map) {
        var _this = this;
        _super.call(this, options);
        this.started = false;
        this.startedEvents = ['modifystart', 'modifyend'];
        this.pointerCoordinate = [];
        this.pixelTolerance_ = 15;
        this.features_ = options.features;
        this.pixelTolerance_ = options.pixelTolerance !== undefined ? options.pixelTolerance : 15;
        this['handleDownEvent_'] = function (mapBrowserEvent) {
            var ret = _this.isPointerNearSelectedVertex(mapBrowserEvent.pixel);
            if (ret) {
                _this.dispatchEvent(new ol.interaction.ModifyEvent('modifystart', _this.features_, mapBrowserEvent));
            }
            return ret;
        };
        this['handleUpEvent_'] = function (mapBrowserEvent) {
            var ret = false;
            if (!ret) {
                _this.dispatchEvent(new ol.interaction.ModifyEvent('modifyend', _this.features_, mapBrowserEvent));
            }
            return ret;
        };
        // We only want to move existing vertices so no highlight and
        // modification of edges or creation of new vertices.
        this['handleEvent'] = function (mapBrowserEvent) {
            if (!(mapBrowserEvent instanceof ol.MapBrowserPointerEvent))
                return true;
            _this.pointerCoordinate = mapBrowserEvent.coordinate;
            if (!_this.isStarted() && !_this.isPointerNearSelectedVertex(mapBrowserEvent.pixel)) {
                return true;
            }
            ;
            // default handlers
            ol.interaction.Pointer.handleEvent.call(_this, mapBrowserEvent);
            return false;
        };
        this['handleDragEvent_'] = function (mapBrowserEvent) {
            // preserve the rectangular shape while modifying the feature
            var map = _this.getMap();
            _this['features_'].forEach(function (feature) {
                var geo = feature.getGeometry();
                if (geo.getType() === 'Polygon' || geo.getType() === 'MultiPolygon') {
                    // e.g. [482.52956397333946, -233.56917532670974, 810.2463886407656, -40.794572581164886]
                    var xt2 = geo.getExtent();
                    var xt = [
                        _this.pointerCoordinate[0],
                        _this.pointerCoordinate[1],
                        Math.abs(xt2[0] - _this.pointerCoordinate[0]) > Math.abs(xt2[2] - _this.pointerCoordinate[0]) ? xt2[0] : xt2[2],
                        Math.abs(xt2[1] - _this.pointerCoordinate[1]) > Math.abs(xt2[3] - _this.pointerCoordinate[1]) ? xt2[1] : xt2[3]
                    ];
                    var coordinates = [[
                            [xt[0], xt[1]],
                            [xt[0], xt[3]],
                            [xt[2], xt[3]],
                            [xt[2], xt[1]],
                            [xt[0], xt[1]]
                        ]];
                    //                    var s = '';
                    //                    coordinates[0].map((p) => {
                    //                        s += '(' + p[0] + ',' + p[1] + '), ';
                    //                    });
                    geo.setCoordinates(coordinates, geo.getLayout());
                }
            });
        };
    }

    /**
     * Returns true if the pointer is near one of the vertices of a selected
     * feature.
     * 'near' means within this.pixelTolerance pixels.
     */
    Modify.prototype.isPointerNearSelectedVertex = function (pointerxy) {
        var _this = this;
        var ret = false;
        var map = this.getMap();
        this['features_'].forEach(function (feature) {
            var geo = feature.getGeometry();
            if (geo.getType() === 'Polygon' || geo.getType() === 'MultiPolygon') {
                var fcs = geo.getFlatCoordinates();
                for (var i = 0; i < fcs.length; i += 2) {
                    var fcxy = map.getPixelFromCoordinate([fcs[i], fcs[i + 1]]);
                    var dist = Math.sqrt(ol.coordinate['squaredDistance'](fcxy, pointerxy));
                    if (dist <= _this['pixelTolerance_']) {
                        ret = true;
                        // show the resize pointer to indicate that Modify mode works
                        var elem = _this.getMap().getTargetElement();
                        elem['style'].cursor = 'move';
                    }
                }
            }
        });
        return ret;
    };
    return Modify;
}(ol.interaction.Pointer));

    initModifyInteraction = function () {
        //Clear interactions
        olpage.removeInteraction(annotationInteraction);
        olpage.removeInteraction(noteSelectInteraction);
        olpage.addInteraction(Modify)
    }

    /**
     * Ends any existing interactions, instantiates an ol.interaction.Draw event to add a note shape.
     * Adds new interation to map.
     * @param noteType Circle or Polygon (for box)
     */
    initDrawInteraction = function (noteType) {
        olpage.removeInteraction(annotationInteraction);
        olpage.removeInteraction(noteSelectInteraction);
        //Create annotation
        var type;
        var drawOptions;
        //Ensure the right layers are visible
        commentLayer.setVisible(false);
        noteLayer.setVisible(true);
        barLayer.setVisible(false);
        if (noteType == "Polygon" || noteType == "Circle") {
            if (noteType == "Polygon") {
                //type = ol.geom.Polygon;
                maxPoints = 2;
                geometryFunction = function (coordinates, geometry) {
                    if (!geometry) {
                        geometry = new ol.geom.Polygon(null);
                    }
                    var start = coordinates[0];
                    var end = coordinates[1];
                    geometry.setCoordinates([
                        [start, [start[0], end[1]], end, [end[0], start[1]], start]
                    ]);
                    return geometry;
                };
                drawOptions = {
                    type: 'LineString',
                    layers: [noteLayer],
                    geometryFunction: geometryFunction,
                    source: noteSource,
                    maxPoints: maxPoints,
                    geometryName: "Box"

                }

            } else if (noteType == "Circle") {
                type = 'Circle';
                drawOptions = {
                    layers: [noteLayer],
                    type: (type),
                    source: noteSource,
                    geometryName: "Circle"
                }
            }
            annotationInteraction = new ol.interaction.Draw(drawOptions);
            annotationInteraction.on('drawend', finishDraw);
        } else if (noteType == "Bar") {
            //Actually a select on the bar layer, not draw
            noteLayer.setVisible(false);
            barLayer.setVisible(true);
            annotationInteraction = new ol.interaction.Select({
                condition: ol.events.condition.click,
                layers: [barLayer],
                multi: true
            });


        }
        olpage.addInteraction(annotationInteraction);
        //todo Check if form is visible, make visible if not

    }

    /**
     * When ol.interaction.Draw triggers draw end, this event finds the geometry
     * of the drawn shape and adds it to the note form.
     * @param event event object passed by Draw
     */
    finishDraw = function (event) {
        var feature = event.feature
        var format = new ol.format.GeoJSON();
        var geometryName = feature.getGeometryName();

        if (geometryName == "Circle") {
            //No circle in GeoJSON, use fromCircle as workaround
            var circle = ol.geom.Polygon.fromCircle(feature.getGeometry());
            var nf = new ol.Feature({ geometry: circle })
            $('#id_noteregions').val(format.writeFeature(nf));

        } else if (geometryName == "Box") {
            $('#id_noteregions').val(format.writeFeature(feature));
        }

        //Add shape id to note form        
        $('#featureid').val(feature.id);


    }

    toggleCommentary = function () {

        if (commentLayer.getVisible() == false) {
            commentLayer.setVisible(true);
        } else {
            commentLayer.setVisible(false);
        }

    }

    toggleExistingNotes = function () {

        if (noteLayer.getVisible() == false) {
            noteLayer.setVisible(true);
        } else {
            noteLayer.setVisible(false);
        }

    }

    /************************************************************************
     * Note form functions
     *
     */

    saveNote = function () {
        //Are bars in the bar layer selected?
        var barString = "";
        if (barLayer.getFeatures().getArray().length > 0) {
            var barFeatures = barLayer.getFeatures().getArray();
            for (var v in barFeatures) {
                //Serialize
                if (barString.length > 0) {
                    barString += ",";
                }
                barString += barFeatures[v].getProperties().barid;
            }
        }

        //Add to form
        $('#noteBars').val(barString);

        //Validate
        if ($('#noteBars').val().length == 0
            && $('#id_noteregions').val().length == 0) {
            //No regions or bars select
            alert('Please attach a bar or draw a shape for your note');
            return false;
        }

        if ($('#id_notetext').val().length == 0) {
            //No Annotation text
            alert('No text written for annotation');
            return false;
        }
    }

    updateUserNote = function (note, notetext) {
        $(note).child('div.annotation p').html(notetext);
    }

    return initMap(ol);
});
