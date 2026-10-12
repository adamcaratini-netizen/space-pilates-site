(function () {
        // Set tenant name here
        var TENANT_NAME = 'space';

        var d = document;
        var sA = ['polyfills', 'js'];

        for (var i = 0; i < sA.length; i++) {
            var s = d.createElement('script');
            s.src = 'https://' + TENANT_NAME + '.marianaiframes.com/' + sA[i];
            s.setAttribute('data-timestamp', +new Date());
            (d.head || d.body).appendChild(s);
        }
    })();
