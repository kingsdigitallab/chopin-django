/********
 *
 * Chopin project Annotation functions
 * ol 3 version
 * Elliott Hall 15/2/2016
 *
 * This script uses the ol 3 library to annotation a single jp2 page of music, with a vector layer representing the bar boxes
 * drawn on top.  Boxes are clickable to link to single bar view.
 * Used in OCVE part of Chopin only.
 *
 *todo: Annotations

 */

define(["jquery", "ol3","pageview-ol3"], function($, ol,pageview) {

    //Remove the default select control
    //And add controls for creating, manipulating and deleting(?) notes
    addAnnotationControls=function(){

    }

    //Fetch the annotations as GeoJSON and add as separate layer to olpage
    addAnnotationLayer=function(){

    }

    //Change controls from bar view selection to note creations
    initAnnotationMode=function(){

    }

    //Load the annotation layer
    initAnnotationView=function(){

    }

});