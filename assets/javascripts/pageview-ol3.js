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

    ol3 = ol;
    var hover;
    //Bars defined by the databaase 
    //for selection to bar view and in annotation attaching notes
    var barLayer;
    //User annotations
    var noteLayer;
    // OCVE critical commentary
    var commentLayer;    
    var olpage;
    var styles;
    // Drawing new annotations
    var annotationInteraction;
    // Drag or resize interatcion
    
    var noteSelectInteraction;
    var noteSource;

    //The Open Layers bar styles
    // invisible: default setting for bar regions
    // hover: For displaying bar number and boundary on hover
    // visibleNote: Annotation
    // selectedNote: Annotation selected
    var initStyles = function () {
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
                    var paddingX = 55;
                    var paddingY = 40;
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
                        font: '14px Courier New, monospace',
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
    var initBarLayer = function () {
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
    //Clickthrough to bar view by click interaction
    initInteractions = function () {

       hover = new ol.interaction.Select({
           //addCondition: ol.events.condition.click,
           condition: ol.events.condition.pointerMove,
           layers: [barLayer],
           style: styles.hover
       });  

       click = new ol.interaction.Select({
           condition: ol.events.condition.click,
           //condition: ol.events.condition.pointerMove,
           layers: [barLayer],
           style: styles.hover
       });  

       click.on('select', function (e) {
            var feature = e.selected[0];
             if (feature) {                     
                     console.log(feature.get('label'));
                     window.location = '/ocve/browse/barview?workid=' + pageimage.workid + '&pageimageid=' + pageimage.pageID + '&barid=' + feature.get("barid");
                 }
        });
       olpage.addInteraction(hover);
       olpage.addInteraction(click);
        
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
                }),
                zoomOptions:({
                    duration : 1000
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
        olpage.addControl(new ol.control.FullScreen());
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
                
        }

        return olpage;
    }


    /* Annotation Functions
     Notes can be attached to three different shapes: a bar region, a drawn square and a drawn circle
     */


    var initAnnotationLayer = function (visible) {
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

    var initCommentLayer = function (visible) {
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

    var initAnnotationInteractions = function () {

        //
        //Bind annotation events to elements
        if ($('#newNoteForm').length > 0) {


            //Bind annotation tool events            
            $(pageimage.barAttachToggle).click(function () {
                initDrawInteraction("Bar");
            });

            $(newSquareNoteToggle).click(function () {
                initDrawInteraction("Polygon");
            });
            $(newCircleNoteToggle).click(function () {
                initDrawInteraction("Circle");
            });
            $('#modifyNoteToggle').click(function () {
                initModifyInteraction("Modify");
            });
            $('#moveNoteToggle').click(function () {
                initModifyInteraction("Move");
            });
            //

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
            
        });
    }

    var endDrawInteraction = function () {
        //remove any existing interaction
        olpage.removeInteraction(annotationInteraction);
        olpage.addInteraction(noteSelectInteraction);
    }


    /**
     * Based on Geoffroy's modify interaction from Digipal
     *
     * https://github.com/kcl-ddh/digipal/blob/master/digipal_text/static/digipal_text/viewer/annotation.ts
     */

     var Modify = function(opt_options) {
        var options = opt_options || {};
        //var _this = this;        
        this.started = false;
        this.startedEvents = ['modifystart', 'modifyend'];
        this.pointerCoordinate = [];
        this.pixelTolerance_ = 15;
        this.features_ = options.features;
        this.layer=options.layers[0];
        this.pixelTolerance_ = options.pixelTolerance !== undefined ? options.pixelTolerance : 15;
        this.vertexMode = "";
        this.circleDist=0;
        this.centreX=0;
        this.centreY=0;
        

        ol.interaction.Pointer.call(this, {
            //handleEvent: Modify.prototype.handleEvent,
          handleDownEvent: Modify.prototype.handleDownEvent,
          handleUpEvent: Modify.prototype.handleUpEvent,
          handleDragEvent: Modify.prototype.handleDragEvent
        });
        this.features_ = options.features;

      };
      ol.inherits(Modify, ol.interaction.Pointer);

      Modify.prototype.handleDownEvent = function (mapBrowserEvent) {
            
            var ret = false;
            if (this.features_){
                // console.log(this.features_.getArray());
                // var props = this.features_.getArray()[0].getProperties();
                // var geometryName=props['geometryName'];
                var ret = this.isPointerNearSelectedVertex(mapBrowserEvent.pixel);

                if (ret) {
                    //this.dispatchEvent(new ol.interaction.Modify.Event('modifystart', this.features_, mapBrowserEvent));         
                    //console.log(mapBrowserEvent.coordinate);
                    this.pointerCoordinate = mapBrowserEvent.coordinate;
                    this.coordinate_ = mapBrowserEvent.coordinate;

                    var Extent = this.features_.getArray()[0].getGeometry().getExtent();
                    this.centreX = Extent[0] + (Extent[2]-Extent[0])/2;
                    this.centreY = Extent[1] + (Extent[3]-Extent[1])/2;
                    this.circleDist = Math.sqrt(Math.pow((mapBrowserEvent.coordinate[1]-this.centreY),2)+Math.pow((mapBrowserEvent.coordinate[0]-this.centreX),2));
                  }
            }
            return ret;
        };
      Modify.prototype.handleUpEvent = function (mapBrowserEvent) {
            var ret = false;
            if (!ret) {
                //this.dispatchEvent(new ol.interaction.Modify.Event('modifyend', this.features_, mapBrowserEvent));
                finishModify(mapBrowserEvent);
            }
            return ret;
        };
        // We only want to move existing vertices so no highlight and
        // modification of edges or creation of new vertices.
       Modify.prototype.handleEvent = function (mapBrowserEvent) {
            if (!(mapBrowserEvent instanceof ol.MapBrowserEvent))
                return true;
            this.pointerCoordinate = mapBrowserEvent.coordinate;
            if (!this.started && !this.isPointerNearSelectedVertex(mapBrowserEvent.pixel)) {
                return true;
            }
            ;
            // default handlers
            ol.interaction.Pointer.handleEvent.call(this, mapBrowserEvent);
            return false;
        };

    Modify.prototype.handleDragEvent = function (mapBrowserEvent) {       

        var this_ = this;
        this.features_.forEach(
            //if circle/rectangle
            function (feature) {
                var geometry = /** @type {ol.geom.SimpleGeometry} */
                    (feature.getGeometry());
                var coord = geometry.getCoordinates()[0];                
                if (coord.length > 5){
                    this_.handleCircleDragEvent(mapBrowserEvent);    
                }else{
                    //Rectangle
                   this_.handlePolygonDragEvent(mapBrowserEvent);    
                }                
                
            }
        );
        
        
        
    }

    Modify.prototype.handleCircleDragEvent = function(mapBrowserEvent){
        var dist = 0;
        var circleDist=this.circleDist;
        var centreX=this.centreX;
        var centreY=this.centreY;
        //Get centre of polygon circle
        
        this.features_.forEach(
            function (feature) {
                //Crile that has been saved
                //and thus transformed into poygon ring
                var geometry = /** @type {ol.geom.SimpleGeometry} */
                    (feature.getGeometry());
                var coord = geometry.getCoordinates();
                var Extent = feature.getGeometry().getExtent();
                var radius = Extent[2] - centreX;                
                
                    
                    // Apply Delta to radius
                    dist=Math.sqrt(Math.pow((mapBrowserEvent.coordinate[1]-centreY),2)+Math.pow((mapBrowserEvent.coordinate[0]-centreX),2));                    

                    delta=dist-circleDist;
                    console.log(delta);

                    //Use Centre and new radius to generate circle
                    // Convert circle back to linear ring polygon                    
                    var circle = new ol.geom.Circle([centreX,centreY],(radius+delta));
                    var cGeo = ol.geom.Polygon.fromCircle(circle);
                    coord = cGeo.getCoordinates();
                
                geometry.setCoordinates(coord, geometry.getLayout());
                
        });
        
        this.circleDist=dist;
    }

    /**
     *
     *  p0(4)        p3
     *
     *
     *  p1        p2
     *
     * @param mapBrowserEvent
     */
      Modify.prototype.handlePolygonDragEvent = function (mapBrowserEvent) {
            // preserve the rectangular shape while modifying the feature
            var map = this.getMap();
            var pointerCoordinate=this.pointerCoordinate;
            var deltaX = mapBrowserEvent.coordinate[0] - this.coordinate_[0];
            var deltaY = mapBrowserEvent.coordinate[1] - this.coordinate_[1];
            this.features_.forEach(
            function (feature) {
                var geometry = /** @type {ol.geom.SimpleGeometry} */
            (feature.getGeometry());
            var coord = geometry.getCoordinates();
            
            if (this.vertexMode == "topLeft"){
                //Top left drag
                // Affects p0.x,p0.y,p1.x,p3.y                
                coord[0][0][0] += deltaX;
                coord[0][0][1] += deltaY;                
                coord[0][4][0] += deltaX;
                coord[0][4][1] += deltaY;                
                coord[0][1][0] += deltaX;                
                coord[0][3][1] += deltaY;
            } else if (this.vertexMode == "topRight"){
                //Top right drag
                // Affects p3.x,p3.y,p2.x,p0.y,p4.y
                coord[0][3][0] += deltaX;
                coord[0][3][1] += deltaY;                
                coord[0][2][0] += deltaX;
                coord[0][0][1] += deltaY;                                
                coord[0][4][1] += deltaY;                               

            }else if (this.vertexMode == "bottomLeft"){
                //Bottom Left
                //Affects p0.x,p4.x,p1.x.p1.y.p2.y
                coord[0][0][0] += deltaX;
                coord[0][4][0] += deltaX;
                coord[0][1][0] += deltaX;               
                coord[0][1][1] += deltaY;
                coord[0][2][1] += deltaY;

            }else if (this.vertexMode == "bottomRight"){
                //Bottom Right
                //Affects p2.x,p2.y,p3.x,p1.y
                coord[0][2][0] += deltaX;
                coord[0][2][1] += deltaY;
                coord[0][3][0] += deltaX;
                coord[0][1][1] += deltaY;
            }

            //Apply new coordinates
            geometry.setCoordinates(coord, geometry.getLayout());

            });
            


            this.coordinate_[0] = mapBrowserEvent.coordinate[0];
            this.coordinate_[1] = mapBrowserEvent.coordinate[1];
            
        };

      

      /**
     * Returns true if the pointer is near one of the vertices of a selected
     * feature.
     * 'near' means within this.pixelTolerance pixels.
     */
    Modify.prototype.isPointerNearSelectedVertex = function (pointerxy) {
        //var this = this;
        var ret = false;
        var map = this.getMap();
        var tolerance = this.pixelTolerance_ 
        var layer = this.layer;     

       // var features = [];
        this.features_.forEach(
            function (feature) {
            var geo = feature.getGeometry();
            if (geo.getType() === 'Polygon' || geo.getType() === 'MultiPolygon') {
                var fcs = geo.getCoordinates()[0];
                if (fcs.length > 5) {
                    // var features=layer.getSource().getFeaturesAtCoordinate(pointerxy);
                    // map.forEachFeatureAtPixel(map.getPixelFromCoordinate(pointerxy),function(f){
                    //         console.log(f);
                    // });
                    
                    // for (var x=0;x<features.length;x++){
                    //     if (feature==features[x]){
                    //         ret=true;
                    //         breal;
                    //     }
                    // }
                    ret = true;
                } else {
                    for (var i = 0; i < fcs.length; i ++) {
                        var point=fcs[i]
                        var fcxy = map.getPixelFromCoordinate(point);
                        var dist = Math.sqrt(squaredDistance(fcxy, pointerxy));
                        
                        if (dist <= tolerance) {
                            ret = true;
                            // show the resize pointer to indicate that Modify mode works
                            
                            // Set the selected vertex to modify correct coordinates
                            if (i ==0 || i ==4){
                                this.vertexMode = "topLeft";
                            }else if (i ==1){
                                this.vertexMode = "bottomLeft";
                            }else if (i ==2){
                                this.vertexMode = "bottomRight";
                            }else if (i ==3){
                                this.vertexMode = "topRight";
                            }
                            console.log(this.vertexMode);
                        }
                    }
                }
                //features.push(feature);
            }
        });                
        //this.features_=features;
        if (ret){
            var elem = map.getTargetElement();
                            elem['style'].cursor = 'move';
        }
        return ret;
    };

    /**Taken from a different version of ol3.  Not in stable one being used.
 * @param {ol.Coordinate} coord1 First coordinate.
 * @param {ol.Coordinate} coord2 Second coordinate.
 * @return {number} Squared distance between coord1 and coord2.
 */
  var squaredDistance = function(coord1, coord2) {
  var dx = coord1[0] - coord2[0];
  var dy = coord1[1] - coord2[1];
  return dx * dx + dy * dy;
};

/**
 * [initModifyInteraction 
 * Instantiate interactions to move or modify an existing note shape
 * @param  {[type]} mode Type of interaction e.g. modify/draft
 * 
 */
    var initModifyInteraction = function (mode) {
        //Clear interactions
        olpage.removeInteraction(annotationInteraction);
        

        //This version of select populates the form on the left
        noteModifySelectInteraction = new ol.interaction.Select({
            features: noteSelectInteraction.getFeatures(),
            filter : function(feature, layer){
                props=feature.getProperties();     
                if (props['userid'] && props['userid'] == $('#id_user').val()){
                    console.log(props);
                            return true;
                        } else{
                            return false;
                        }
            }
            
        }); 
        noteModifySelectInteraction.on('select', modifySelect);
        olpage.removeInteraction(noteSelectInteraction);  
        olpage.addInteraction(noteModifySelectInteraction);

        if (mode == 'Move'){
            annotationInteraction = new ol.interaction.Translate({
                features: noteSelectInteraction.getFeatures()
            });
            annotationInteraction.on('translateend', finishModify);       
        }else if (mode == 'Modify'){
        
        var modifyOptions = {
                    layers: [noteLayer],                    
                    source: noteSource, 
                    features: noteSelectInteraction.getFeatures()                   
                }
        
        
        annotationInteraction = new Modify(modifyOptions);
        
        }
        olpage.addInteraction(annotationInteraction);
    }

    /**
     * Select Event for modify select interaction
     * To update the form on right 
     * @param  {[type]} event [description]
     * @return {[type]}       [description]
     */
    var modifySelect = function(event){
        //todo Only allow select of user's note
        var features = noteSelectInteraction.getFeatures();        
        if (features){            
            var feature = features.getArray()[0];   
            var noteid = feature.getProperties().noteid;            
            console.log(feature.getProperties().barid);
            if (noteid > 0){
                var text=$('#comment-'+noteid+' div.annotation p').html();
                var noteTypeid = $('#comment-'+noteid+' div.annotation').data('notetype'); 
                $('#id_type').val(noteTypeid);            
                $('#id_notetext').val(text);
                $('#annotation_id').val(noteid);
            }else{
                $('#annotation_id').val(0);
                $('#id_notetext').val('');

            }
            if (feature.getProperties().barid != undefined){
                //Bar note selected for modify
                //Go back to bar select interaction
                initDrawInteraction("Bar");
                //select current bar.               

            }else{
            
            updateFormGeometry(feature);
            }
        }
    }

    var finishModify = function(event) {
        var features = noteSelectInteraction.getFeatures();        
        if (features){            
            var feature = features.getArray()[0];            
            updateFormGeometry(feature);    
        }
        
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
    var finishDraw = function (event) {
        var feature = event.feature;                
        updateFormGeometry(feature);
    }

    /**
     * Update the note form with geomertry of selected feature
     * Modified or newly created
     * 
     * @param  {[type]} feature [description]
     * @return {[type]}         [description]
     */
    updateFormGeometry = function (feature){
        var format = new ol.format.GeoJSON();
        var geometryName = feature.getGeometryName();        
        /*if (geometryName == 'geometry'){
            //EXisting note, get geometryname from geojson
            var props = feature.getProperties();
            geometryName=props['geometryName'];
        }
        console.log(format.writeFeature(feature));*/
        
        if (feature.getGeometry() instanceof ol.geom.Circle) {
            
            //No circle in GeoJSON, use fromCircle as workaround
            var circle = ol.geom.Polygon.fromCircle(feature.getGeometry());            
            feature.setGeometry(circle);            
            var nf = new ol.Feature({ geometry: circle })            
            $('#id_noteregions').val(format.writeFeature(nf));

        } else  {
            $('#id_noteregions').val(format.writeFeature(feature));
        }

        //Add shape id to note form        
        $('#featureid').val(feature.id);
        console.log('Form Updated');
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
        if (annotationInteraction.getFeatures().getArray().length > 0) {
            var barFeatures = annotationInteraction.getFeatures().getArray();
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


