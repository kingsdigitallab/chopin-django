/**
 * Created by elliotthall on 15/02/16.
 */

requirejs.config({
    paths: {
        vendor: '../vendor',
        ol3: '../vendor/OpenLayers/3.18.2/ol',
        jquery: '../vendor/jquery/dist/jquery'
    },
    shim: {
        "pageview-ol3": ["jquery","ol3"]

    }
});

requirejs(["jquery","ol3","pageview-ol3"], function($,ol,pageview) {

    'use strict';

  $(document).ready(function() {
    // load map
    //pageview.initMap(ol);
      //joyride

  });


});

