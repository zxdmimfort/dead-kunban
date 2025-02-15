// Global variables for React and ReactDOM
const { useState, useEffect, useRef } = React;

function MenuComponent() {
    // State variables
    const [isCursorLocked, setIsCursorLocked] = useState(false);
    const [lazy, setLazy] = useState(true);
    const [pointerPosition, setPointerPosition] = useState({ x: 0, y: 0 });

    // Refs for DOM elements
    const cursorRef = useRef(null);
    const radialMenuRef = useRef(null);
    const svgRef = useRef(null);
    const pieRef = useRef(null);
    const sliceRef = useRef(null);
    const hintRef = useRef(null);
    const blackoutRef = useRef(null);

    // Frozen coordinates state
    const [frozenCoordinates, setFrozenCoordinates] = useState({ x: 0, y: 0 });

    // Utility functions
    function showGently(element) {
        if (element) {
            element.style.opacity = '0';
            element.style.display = '';
            element.style.transition = 'opacity 0.5s';
            setTimeout(() => {
                element.style.display = 'inline';
                element.style.opacity = '1';
            }, 100);
        }
    }

    function hideGently(element) {
        if (element) {
            element.style.opacity = '1';
            element.style.transition = 'opacity 0.5s';
            setTimeout(() => {
                element.style.opacity = '0';
                setTimeout(() => {
                    element.style.display = 'none';
                }, 500);
            }, 100);
        }
    }

    function coerceIn(value, min, max) {
        return Math.max(min, Math.min(max, value));
    }

    // Event handlers
    function updateCursorPosition(e) {
        if (lazy) {
            showGently(cursorRef.current);
            showGently(hintRef.current);
        }

        const limitPie = true;
        const html = document.documentElement;
        const pointer_x = limitPie
            ? coerceIn(e.clientX - 8, 150, html.clientWidth - 150)
            : e.clientX;
        const pointer_y = limitPie
            ? coerceIn(e.clientY - 8, 150, html.clientHeight - 150)
            : e.clientY;

        // Update pointer position only if the cursor is not locked
        if (!isCursorLocked) {
            setPointerPosition({ x: pointer_x, y: pointer_y });
        }

        if (cursorRef.current) {
            cursorRef.current.style.top = `${e.clientY - 10}px`;
            cursorRef.current.style.left = `${e.clientX - 10}px`;
        }

        if (!isCursorLocked || lazy) {
            if (radialMenuRef.current) {
                radialMenuRef.current.style.top = `${e.clientY - 10}px`;
                radialMenuRef.current.style.left = `${e.clientX - 10}px`;
            }
            if (hintRef.current) {
                hintRef.current.style.top = `${e.clientY - 100}px`;
                hintRef.current.style.left = `${e.clientX - 100}px`;
            }
            setLazy(false);
        }

        // Update button positions using either frozen or current coordinates
        const cursorCenterX = pointer_x;
        const cursorCenterY = pointer_y;

        let X = pointerPosition.x-8-svgRef.current.clientWidth/2;
        let Y = pointerPosition.y-8-svgRef.current.clientHeight/2;

        root.style.setProperty('--translatePieX', X + 'px');
        root.style.setProperty('--translatePieY', Y + 'px');

        updateButtonPositions(cursorCenterX, cursorCenterY);
    }

    function toggleMenu() {
        setIsCursorLocked((prev) => {
            if (!prev) {
                // Freeze the current pointer position when locking the cursor
                setFrozenCoordinates(pointerPosition);
                showGently(svgRef.current);
                showGently(pieRef.current);
                showGently(sliceRef.current);
                showGently(radialMenuRef.current);
                showGently(blackoutRef.current);
            } else {
                hideGently(sliceRef.current);
                hideGently(svgRef.current);
                hideGently(pieRef.current);
                hideGently(radialMenuRef.current);
                hideGently(blackoutRef.current);
            }
            return !prev;
        });
    }

    // Function to update button positions
    function updateButtonPositions(cursorCenterX, cursorCenterY) {
        const layers = radialMenuRef.current?.querySelectorAll('.radial-menu-layer');
        if (!layers) return;

        layers.forEach((layer, layer_index) => {
            const buttons = layer.querySelectorAll('button');
            const r0 = 20;
            const offset = 150;
            const radius = r0 + offset * (layer_index + 1);

            buttons.forEach((button, index) => {
                const delta = (2 * Math.PI) / buttons.length;
                const angle_rotate = (3 * Math.PI) / 2;
                const angle =
                    -Math.PI / 2 +
                    ((index / buttons.length) * Math.PI * 2 + angle_rotate);

                const buttonX = -92 + cursorCenterX + Math.cos(angle) * radius;
                const buttonY = -20 + cursorCenterY + Math.sin(angle) * radius;

                button.style.top = `${buttonY}px`;
                button.style.left = `${buttonX}px`;

                // Add hover effect for buttons
                button.onmouseover = () => {
                    const to_percents = (v) => (v * 100) / (2 * Math.PI);
                    const delta_in_percents = to_percents(delta / 2);

                    if (sliceRef.current) {
//                        sliceRef.current.style.strokeDasharray = `${delta_in_percents} 100`;
                        sliceRef.current.style.strokeDasharray= `${to_percents(delta/2)} 100`;
                        sliceRef.current.setAttribute(
                            'transform',
                            `rotate(${180+(180*(angle-delta/4))/Math.PI} 32 32)`
                        );
                    }
                };
            });
        });
    }

    // Effect for initialization
    useEffect(() => {
        const html = document.documentElement;
        const initialEvent = {
            clientX: html.clientWidth / 2,
            clientY: html.clientHeight / 2,
        };
        updateCursorPosition(initialEvent);

        document.addEventListener('mousemove', updateCursorPosition);
        document.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            if (!lazy) toggleMenu();
        });

        return () => {
            document.removeEventListener('mousemove', updateCursorPosition);
        };
    }, [lazy, isCursorLocked]);

    return (
        <div className="menu" style={{ position: 'fixed', zIndex: 999 }}>
            {/* Cursor */}
            <div
                ref={cursorRef}
                className="cursor"
                style={{ zIndex: 999, display: 'none' }}
            ></div>

            {/* SVG Pie */}
            <svg
                ref={svgRef}
                viewBox="0 0 64 64"
                className="pie"
                style={{ display: 'none' }}
            >
                <circle
                    ref={pieRef}
                    id="thepie"
                    r="25%"
                    cx="50%"
                    cy="50%"
                    style={{
                        display: 'none',
                        strokeDasharray: '0 100',
                        strokeDashoffset: '-50',
                    }}
                ></circle>
                <circle
                    ref={sliceRef}
                    id="slice"
                    cx="50%"
                    cy="50%"
                    r="25%"
                    fill="red"
                    style={{
                        display: 'none',
                        strokeDasharray: '0 100',
                        strokeDashoffset: '-50',
                        transform: 'rotate(0 32 32)',
                    }}
                ></circle>
            </svg>

            {/* Radial Menu */}
            <div
                ref={radialMenuRef}
                className="radial-menu"
                style={{ display: 'none' }}
            >
                <div className="radial-menu-layer">
                    <a href="/">
                        <button>Стартовая страница</button>
                    </a>
                    <a href="/masking/">
                        <button>Обфускация PDF</button>
                    </a>
                    <a href="/title/">
                        <button>Генерация титульников</button>
                    </a>
                    <a href="/kanban/">
                        <button>Kanban</button>
                    </a>
                    <a href="/teststyles/">
                        <button>Test styles</button>
                    </a>
                    <a href="/login/">
                        <button>login</button>
                    </a>
                    <a href="/logout/">
                        <button>logout</button>
                    </a>
                </div>
            </div>

            {/* Hint */}
            <div
                ref={hintRef}
                className="hint"
                style={{ display: 'none' }}
            >
                ПКМ / долгий тап
            </div>

            {/* Blackout */}
            <div
                ref={blackoutRef}
                className="blackout"
                style={{ display: 'none' }}
//                onClick={toggleMenu}
            ></div>
        </div>
    );
}


    ReactDOM.render(<MenuComponent />, document.getElementById('root'));