// live2d-widget 简化加载器
(function() {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/live2d-widget@3.1.4/lib/L2Dwidget.min.js';
    script.onload = function() {
        L2Dwidget.init({
            model: {
                jsonPath: '/static/live2d/haru/runtime/haru_greeter_t05.model3.json',
                scale: 1
            },
            display: {
                position: 'left',
                width: 300,
                height: 400,
                hOffset: 0,
                vOffset: -20
            },
            mobile: {
                show: true,
                scale: 0.5
            }
        });
    };
    document.head.appendChild(script);
})();
