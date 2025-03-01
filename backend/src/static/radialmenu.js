    function showGently(elementStyle) {
        elementStyle.opacity = '0';
            elementStyle.display = '';
            elementStyle.transition = 'opacity 0.5s';
            setTimeout(() => {
                elementStyle.display = 'inline';
                elementStyle.opacity = '1';
            }, 100);
    };
    function coerceIn(value, min, max) {
      return Math.max(min, Math.min(max, value));
    }
    function hideGently(elementStyle) {
        elementStyle.opacity = '1';
        elementStyle.transition = 'opacity 0.5s';
        setTimeout(() => {
            elementStyle.opacity = '0';
            setTimeout(() => {
                elementStyle.display = 'none';
            }, 500);
        }, 100);
    };

class MyMenu {
    constructor() {
        this.limitPie = true;
        this.hideCurrentPageLink = false;
        this.lazy = true;

        this.cursor = document.querySelector('.cursor');
        this.radialMenu = document.querySelector('div.radial-menu');
        this.blackout = document.querySelector('.blackout');
        this.html = document.querySelector('html');
        this.layers = document.querySelectorAll('.radial-menu-layer');
        this.hint = document.querySelector('div.hint');
        this.title = document.querySelector('h1#title');
        this.isCursorLocked = false;
        this.svg = document.querySelector('svg.pie');
        this.pie = document.querySelector('#thepie');
        this.slice = document.querySelector('#slice');
        if (this.hideCurrentPageLink) {
            this.currentPage = document.querySelector(`a[href="\\${window.location.pathname}"]`);
            this.currentPage.remove();
        }
        this.pie.style.strokeDashoffset = `0`;
        this.pie.style.strokeDasharray= `0 100`;
        this.pointer_x = 0;
        this.pointer_y = 0;
    }


    updateButtonPositions() {
//        const cursorRect = this.cursor.getBoundingClientRect();
        const cursorCenterX = this.pointer_x;
        const cursorCenterY = this.pointer_y;

        this.layers.forEach((layer, layer_index) => {
            const buttons = layer.querySelectorAll('button');
            var r0 = 20;
            let offset = 150;
            var radius = r0+(offset * (layer_index + 1));
            buttons.forEach((button, index) => {
                const delta = (2 * Math.PI / (buttons.length));
                const angle_rotate = 3*Math.PI/2;
                const angle = -Math.PI/2 + ((index) / buttons.length) * Math.PI * 2+ angle_rotate;
                const buttonX =  -92 +cursorCenterX + Math.cos(angle) * radius;
                const buttonY =  -20 + cursorCenterY + Math.sin(angle) * radius;

                button.delta = delta;
                button.style.top = buttonY + 'px';
                button.style.left = buttonX + 'px';

                button.angle_rad = angle;
                button.a0 = 0;
                button.an = angle_rotate+ ((index) / buttons.length) * Math.PI * 2;
                button.radius = radius;
                button.x = buttonX;
                button.y = buttonY;

                button.addEventListener('mouseover', e=> {
                    let button = e.target;
                    const to_percents = (v) => v*100.  / (2*Math.PI);
                    let delta_in_percents = to_percents(button.delta/2);


                    this.slice.style.strokeDasharray= `${to_percents(button.delta/2)} 100`;
                    this.slice.setAttribute('transform', `rotate(${ 90+180*(button.an-button.delta/4+button.a0)/Math.PI } 32 32)`);
                });
            });
        });
    }



    hide(elementStyle) {
        elementStyle.opacity = '0';
        elementStyle.display = 'none';
    }

    update_transform()
    {
        const root = document.documentElement;
        let X = this.pointer_x-8-this.svg.clientWidth/2;
        let Y = this.pointer_y-8-this.svg.clientHeight/2;
        root.style.setProperty('--translatePieX', X + 'px');
        root.style.setProperty('--translatePieY', Y + 'px');

//        this.svg.setAttribute('transform', `translate(${X}, ${Y})`);
    }

    toggleMenu()
    {

            if (!this.isCursorLocked) {
                this.isCursorLocked = true;
                showGently(this.svg.style);
                this.update_transform();
                showGently(this.pie.style);
                showGently(this.slice.style);
                showGently(this.radialMenu.style);
                showGently(this.blackout.style);

                this.layers.forEach((layer, index) => {
                    showGently(layer.style);
                })

            } else {
//                setTimeout(() => {
                    this.isCursorLocked = false;
//                }, 500);

                hideGently(this.slice.style);
                hideGently(this.svg.style);
                hideGently(this.pie.style);
                hideGently(this.radialMenu.style);
                hideGently(this.blackout.style);

                this.layers.forEach((layer, index) => {
                    hideGently(layer.style);
                })
            }
        }

        update_cursor_and_menu(e) {
            if (this.lazy) {
                showGently(this.cursor.style);
                showGently(this.hint.style)
            }

            if (this.limitPie) {
                this.pointer_x = coerceIn(e.clientX-8, 150, this.html.clientWidth-150);
                this.pointer_y = coerceIn(e.clientY-8, 150, this.html.clientHeight-150);
            } else {
                this.pointer_x = e.clientX;
                this.pointer_y = e.clientY;
            }

            this.cursor.style.top = (e.clientY-10) + 'px';
            this.cursor.style.left = (e.clientX-10) + 'px';


            if (!this.isCursorLocked || this.lazy){
                this.radialMenu.style.top = (e.clientX-10) +'px';
                this.radialMenu.style.left = (e.clientY-10) +'px';
                this.hint.style.top = (e.clientY-100) + 'px';
                this.hint.style.left = (e.clientX-100) + 'px';

                this.updateButtonPositions();
                this.lazy = false;
            }
        }

    init() {

       class EventMock {
         constructor(html) {
           this.clientX = html.clientWidth/2;
           this.clientY = html.clientHeight/2;
         }
       }
        this.update_cursor_and_menu(new EventMock(this.html))
        this.html.addEventListener('mousemove', e => {
            this.update_cursor_and_menu(e)
        });
        function debounce(callback, delay) {
          let timer;
          return function() {
            clearTimeout(timer)
            timer = setTimeout(() => {
              callback();
            }, delay)
          }
        }
        document.addEventListener('contextmenu', e => {
            event.preventDefault(); if (!this.lazy) this.toggleMenu();
        });

        var touchduration = 500;

        function touchstart(onlongtouch) {
            var timer = setTimeout(onlongtouch, touchduration);
        }

        function touchend() {
            if (timer)
                clearTimeout(timer);
        }

        document.addEventListener('touchstart', (e) => {touchstart( this.toggleMenu )} );
        document.addEventListener('touchend', e => {touchend()} );

        this.blackout.addEventListener('click', e => {
            this.toggleMenu();
        })
    }
}   ;

const myObject = new MyMenu();
myObject.init();
//if (window.location.pathname == "/") {
//    myObject.toggleMenu();
//}

