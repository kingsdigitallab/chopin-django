/**
 * Created by elliotthall on 15/02/16.
 */

requirejs.config({
    //By default load any module IDs from js/lib
    //baseUrl: 'js/lib',
    //except, if the module ID starts with "app",
    //load it from the js/app directory. paths
    //config is relative to the baseUrl, and
    //never includes a ".js" extension since
    //the paths config could be for a directory.
    paths: {
        vendor: '../vendor',
        ol3: '../vendor/ol v3.13.1/build/ol',
        jquery: '../vendor/jquery/dist/jquery'
    }
});

requirejs(["jquery","ol3","pageview-ol3"], function($,ol,pageview) {
    //This function is called when scripts/helper/util.js is loaded.
    //If util.js calls define(), then this function is not fired until
    //util's dependencies have loaded, and the util argument will hold
    //the module value for "helper/util".
    'use strict';

  $(document).ready(function() {
    // load map
    //pageview.initMap(ol);
  });


});

