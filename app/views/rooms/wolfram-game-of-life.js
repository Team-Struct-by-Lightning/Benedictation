
<canvas width="650" height="365" class="nofade" id="latency"></canvas>
</div>
<!-- end solutions -->
<script>
    (function() {
        var F = 0;
        var E = ["ms", "moz", "webkit", "o"];
        for (var D = 0; D < E.length && !window.requestAnimationFrame; ++D) {
            window.requestAnimationFrame = window[E[D] + "RequestAnimationFrame"];
            window.cancelAnimationFrame = window[E[D] + "CancelAnimationFrame"] || window[E[D] + "CancelRequestAnimationFrame"]
        }
        if (!window.requestAnimationFrame) {
            window.requestAnimationFrame = function(A, I) {
                var J = window.performance && window.performance.now ? (performance.now() + performance.timing.navigationStart) : Date.now();
                var C = Math.max(0, 16 - (J - F));
                var B = window.setTimeout(function() {
                    A(J + C)
                }, C);
                F = J + C;
                return B
            }
        }
        if (!window.cancelAnimationFrame) {
            window.cancelAnimationFrame = function(A) {
                clearTimeout(A)
            }
        }
    }());
    String.prototype.hashCode = function() {
        var E = 0;
        var F = null;
        if (this.length === 0) {
            return E
        }
        for (var D = 0; D < this.length; D++) {
            F = this.charCodeAt(D);
            E = ((E << 5) - E) + F;
            E = E & E
        }
        return E
    };

    function LatencyAnimation() {
        this.animationInterval = null;
        this.animationTimeout = null;
        this.animationFram = null;
        this.lastTime = window.performance && window.performance.now ? (performance.now() + performance.timing.navigationStart) : Date.now();
        this.displayCanvas = null;
        this.displayCanvasContext = null;
        this.renderCanvas = null;
        this.renderCanvasContext = null;
        this.alive = null;
        this.canvasParent = document.getElementById("solutions");
        this.size = 9;
        this.stepDelay = 100;
        this.iterations = 0;
        this.dots = new Array();
        this.containerWidth = Math.min(this.canvasParent.offsetWidth, (window.innerWidth > 0) ? window.innerWidth : screen.width);
        this.renderHeight = this.containerWidth;
        this.displayHeight = this.containerWidth * 9 / 16;
        this.rows = Math.floor(this.renderHeight / (this.size + 1));
        this.cells = Math.floor(this.containerWidth / (this.size + 1));
        this.rowPadding = 0;
        this.births = [3, 5, 7];
        this.survivors = [3, 4, 5, 7];
        this.generations = 5;
        this.colors = ["#eee", "#ddd", "#ccc", "#bbb", "#aaa", "#999", "#888", "#777"];
        this.globalOpacity = 10;
        this.displayCanvas = document.createElement("canvas");
        this.seedList = [
            [
                [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                [0, 2, 1, 1, 1, 1, 0, 0, 0, 0],
                [1, 1, 3, 4, 2, 1, 1, 0, 0, 0],
                [0, 1, 1, 1, 4, 1, 1, 0, 0, 0],
                [0, 1, 2, 0, 1, 1, 1, 1, 0, 0],
                [0, 1, 1, 1, 0, 0, 2, 2, 0, 0],
                [0, 0, 2, 2, 0, 0, 1, 1, 1, 0],
                [0, 0, 1, 1, 1, 1, 0, 2, 1, 0],
                [0, 0, 0, 1, 1, 4, 1, 1, 1, 0],
                [0, 0, 0, 1, 1, 2, 4, 3, 1, 1],
                [0, 0, 0, 0, 1, 1, 1, 1, 2, 0],
                [0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0, 0, 0, 1, 0],
                [1, 1, 1, 1, 0, 0, 1, 0],
                [0, 1, 0, 0, 1, 1, 1, 1],
                [0, 1, 0, 0, 0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0, 0, 0, 1, 1],
                [0, 0, 1, 1, 1, 0, 1, 1],
                [1, 1, 0, 1, 1, 1, 0, 0],
                [1, 1, 0, 0, 0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0, 0, 0, 1, 1],
                [0, 1, 1, 1, 1, 1, 0, 0],
                [0, 0, 1, 1, 1, 1, 1, 0],
                [1, 1, 0, 0, 0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0, 0, 0, 1, 1],
                [1, 0, 0, 0, 1, 1, 1, 0],
                [0, 1, 1, 1, 0, 0, 0, 1],
                [1, 1, 0, 0, 0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0, 0, 0, 1, 1],
                [1, 0, 0, 1, 1, 0, 1, 1],
                [1, 1, 0, 1, 1, 0, 0, 1],
                [1, 1, 0, 0, 0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0, 1, 1, 1, 0],
                [1, 1, 1, 0, 1, 1, 1, 1],
                [1, 1, 1, 1, 0, 1, 1, 1],
                [0, 1, 1, 1, 0, 0, 0, 0]
            ],
            [
                [0, 0, 1, 1, 1, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 1],
                [1, 1, 1, 0, 1, 1, 0, 1],
                [1, 1, 1, 1, 1, 1, 0, 0]
            ],
            [
                [0, 1, 0, 0, 0, 1, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 1],
                [1, 1, 1, 0, 1, 1, 0, 1],
                [1, 1, 1, 0, 0, 0, 1, 0]
            ],
            [
                [0, 1, 1, 0, 1, 1, 1, 1],
                [0, 1, 0, 1, 0, 0, 1, 0],
                [0, 1, 0, 0, 1, 0, 1, 0],
                [1, 1, 1, 1, 0, 1, 1, 0]
            ],
            [
                [1, 1, 1, 0, 1, 1, 1, 0],
                [0, 1, 0, 0, 1, 1, 1, 0],
                [0, 1, 1, 1, 0, 0, 1, 0],
                [0, 1, 1, 1, 0, 1, 1, 1]
            ],
            [
                [1, 1, 1, 0, 1, 1, 1, 1],
                [1, 1, 0, 1, 1, 1, 1, 0],
                [0, 1, 1, 1, 1, 0, 1, 1],
                [1, 1, 1, 1, 0, 1, 1, 1]
            ],
            [
                [1, 1, 1, 1, 0, 0, 0, 1],
                [1, 1, 0, 1, 1, 0, 0, 1],
                [1, 0, 0, 1, 1, 0, 1, 1],
                [1, 0, 0, 0, 1, 1, 1, 1]
            ],
            [
                [1, 1, 1, 1, 0, 0, 1, 0],
                [0, 0, 1, 0, 1, 1, 0, 1],
                [1, 0, 1, 1, 0, 1, 0, 0],
                [0, 1, 0, 0, 1, 1, 1, 1]
            ],
            [
                [1, 1, 1, 1, 0, 0, 1, 0],
                [1, 0, 0, 1, 1, 0, 1, 1],
                [1, 1, 0, 1, 1, 0, 0, 1],
                [0, 1, 0, 0, 1, 1, 1, 1]
            ],
            [
                [1, 1, 1, 1, 0, 0, 1, 0],
                [1, 1, 1, 0, 1, 0, 0, 1],
                [1, 0, 0, 1, 0, 1, 1, 1],
                [0, 1, 0, 0, 1, 1, 1, 1]
            ],
            [
                [1, 1, 1, 1, 0, 0, 1, 0],
                [1, 1, 1, 0, 1, 1, 0, 1],
                [1, 0, 1, 1, 0, 1, 1, 1],
                [0, 1, 0, 0, 1, 1, 1, 1]
            ],
            [
                [1, 1, 1, 1, 0, 0, 1, 0],
                [1, 1, 1, 1, 0, 0, 1, 1],
                [1, 1, 0, 0, 1, 1, 1, 1],
                [0, 1, 0, 0, 1, 1, 1, 1]
            ],
            [
                [1, 1, 1, 1, 0, 1, 0, 1],
                [1, 1, 1, 0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0, 1, 1, 1],
                [1, 0, 1, 0, 1, 1, 1, 1]
            ],
            [
                [1, 1, 1, 1, 0, 1, 1, 0],
                [0, 0, 0, 0, 0, 1, 1, 0],
                [0, 1, 1, 0, 0, 0, 0, 0],
                [0, 1, 1, 0, 1, 1, 1, 1]
            ],
            [
                [1, 1, 1, 1, 0, 1, 1, 0],
                [0, 1, 0, 0, 1, 0, 1, 0],
                [0, 1, 0, 1, 0, 0, 1, 0],
                [0, 1, 1, 0, 1, 1, 1, 1]
            ],
            [
                [1, 1, 1, 1, 0, 1, 1, 0],
                [1, 1, 1, 0, 0, 1, 1, 0],
                [0, 1, 1, 0, 0, 1, 1, 1],
                [0, 1, 1, 0, 1, 1, 1, 1]
            ],
            [
                [1, 1, 1, 1, 1, 0, 0, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 0, 0, 1, 1, 1, 1, 1]
            ],
            [
                [1, 1, 1, 1, 1, 0, 0, 0],
                [1, 1, 0, 1, 1, 1, 1, 0],
                [0, 1, 1, 1, 1, 0, 1, 1],
                [0, 0, 0, 1, 1, 1, 1, 1]
            ],
            [
                [1, 1, 1, 1, 1, 0, 1, 1],
                [0, 0, 1, 1, 1, 0, 0, 0],
                [0, 0, 0, 1, 1, 1, 0, 0],
                [1, 1, 0, 1, 1, 1, 1, 1]
            ],
            [
                [1, 1, 1, 1, 1, 0, 1, 1],
                [0, 1, 1, 1, 1, 1, 0, 1],
                [1, 0, 1, 1, 1, 1, 1, 0],
                [1, 1, 0, 1, 1, 1, 1, 1]
            ],
            [
                [1, 1, 1, 1, 1, 0, 1, 1],
                [1, 1, 0, 1, 0, 1, 1, 0],
                [0, 1, 1, 0, 1, 0, 1, 1],
                [1, 1, 0, 1, 1, 1, 1, 1]
            ],
            [
                [1, 1, 1, 1, 1, 0, 1, 1],
                [1, 1, 1, 1, 0, 0, 1, 1],
                [1, 1, 0, 0, 1, 1, 1, 1],
                [1, 1, 0, 1, 1, 1, 1, 1]
            ],
            [
                [1, 1, 1, 1, 1, 1, 0, 0],
                [0, 0, 1, 0, 0, 1, 1, 1],
                [1, 1, 1, 0, 0, 1, 0, 0],
                [0, 0, 1, 1, 1, 1, 1, 1]
            ],
            [
                [1, 1, 1, 1, 1, 1, 0, 0],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [0, 0, 1, 1, 1, 1, 1, 1]
            ],
            [
                [1, 1, 1, 1, 1, 1, 1, 0],
                [0, 0, 1, 0, 1, 0, 1, 1],
                [1, 1, 0, 1, 0, 1, 0, 0],
                [0, 1, 1, 1, 1, 1, 1, 1]
            ]
        ];
        this.supportsCanvas = !!(this.displayCanvas.getContext && this.displayCanvas.getContext("2d"));
        this.init = function(H) {
            if (H) {
                this.canvasParent = H
            }
            if (this.supportsCanvas) {
                this.displayCanvas.width = this.containerWidth;
                this.displayCanvas.height = this.displayHeight;
                this.displayCanvas.className = "nofade";
                this.displayCanvasContext = this.displayCanvas.getContext("2d");
                this.displayCanvasContext.globalCompositeOperation = "copy";
                this.displayCanvas.id = "latency";
                this.renderCanvas = document.createElement("canvas");
                this.renderCanvasContext = this.renderCanvas.getContext("2d");
                this.devicePixelRatio = 1, this.backingStoreRatio = this.displayCanvasContext.webkitBackingStorePixelRatio || this.displayCanvasContext.mozBackingStorePixelRatio || this.displayCanvasContext.msBackingStorePixelRatio || this.displayCanvasContext.oBackingStorePixelRatio || this.displayCanvasContext.backingStorePixelRatio || 1, this.ratio = this.devicePixelRatio / this.backingStoreRatio;
                if (!this.ratio) {
                    this.ratio = 1
                }
                this.rows = Math.floor(this.renderHeight / (this.size + 1));
                this.cells = Math.floor(this.containerWidth / (this.size + 1));
                this.renderCanvas.width = this.size + 1;
                this.renderCanvas.height = this.size + 1;
                var L = null;
                var I = Math.floor(this.size / 2) + 0.5;
                var J = I;
                this.dots[0] = null;
                for (var K = 1, G = this.colors.length; K < G; K++) {
                    this.renderCanvasContext.fillStyle = "#fff";
                    this.renderCanvasContext.clearRect(0, 0, this.renderCanvas.width, this.renderCanvas.height);
                    this.renderCanvasContext.fillStyle = this.colors[K];
                    this.renderCanvasContext.beginPath();
                    this.renderCanvasContext.arc(I, J, K < 3 ? 2 : +this.size * (K / this.colors.length), 0, 2 * Math.PI, false);
                    this.renderCanvasContext.closePath();
                    this.renderCanvasContext.fill();
                    L = new Image();
                    L.src = this.renderCanvas.toDataURL();
                    this.dots[K] = L
                }
                this.displayCanvasContext.scale(this.ratio, this.ratio);
                this.renderCanvas.width = this.containerWidth * this.ratio;
                this.renderCanvas.height = this.containerWidth * this.ratio;
                this.displayCanvas.style.display = "";
                this.canvasParent.appendChild(this.displayCanvas)
            } else {
                document.documentElement.className = document.documentElement.className + " noCanvas"
            }
        }, this.center = function(R) {
            var P = 0;
            var O = 0;
            if (R) {
                var P = R.length;
                var O = R[0].length
            }
            var N = this.cells - O;
            var Q = this.rows - P;
            var K = new Array();
            if (N > 1) {
                var J = Math.floor(N / 2);
                var M = new Array(J);
                for (var L = 0; L < P; L++) {
                    K[L] = M.concat(R[L], M)
                }
            } else {
                K = R
            }
            if (Q >= 1) {
                this.rowPadding = Math.floor(Q / 2);
                for (var L = 0; L <= this.rowPadding; L++) {
                    K.unshift(new Array(this.cells));
                    if (K.length != this.cells) {
                        K.push(new Array(this.cells))
                    }
                }
            }
            this.alive = K;
            this.rows = this.alive.length;
            this.cells = this.alive[0].length;
            return K
        }, this.start = function(G, J, K) {
            if (!this.supportsCanvas) {
                return
            }
            var H = this;
            if (G) {
                try {
                    if (typeof G === "object") {
                        G = /[\\?&]i=([^&#]*)/g.exec(G.target.href)[1].hashCode() % this.seedList.length
                    } else {
                        if (typeof G != "string") {
                            G = +G
                        }
                    }
                } catch (I) {
                    G = 0
                }
                this.center(this.seedList[G])
            } else {
                G = +Math.abs(document.getElementById("i").value.hashCode()) % this.seedList.length;
                this.center(this.seedList[G])
            }
            if (typeof J === "number" && J > 0) {
                this.step(J)
            } else {
                this.iterations = 0
            }
            if (K) {
                clearTimeout(this.animationTimeout);
                var L = window.performance && window.performance.now ? (performance.now() + performance.timing.navigationStart) : Date.now();
                window.setTimeout(function() {
                    H.animate(L)
                }, K)
            } else {
                var L = window.performance && window.performance.now ? (performance.now() + performance.timing.navigationStart) : Date.now();
                clearTimeout(this.animationTimeout);
                this.animate(L)
            }
            this.globalOpacity = 10;
            this.displayCanvas.style.display = "";
            this.displayCanvas.style.opacity = ""
        }, this.stop = function() {
            this.displayCanvas.style.display = "";
            clearTimeout(this.animationTimeout);
            cancelAnimationFrame(this.animationFrame);
            this.iterations = 0;
            localStorage.setItem("iterations", this.iterations)
        }, this.animate = function(C) {
            var D = this;
            this.lastTime = C;
            clearTimeout(this.animationTimeout);
            this.animationTimeout = setTimeout(function() {
                cancelAnimationFrame(D.animationFrame);
                D.animationFrame = requestAnimationFrame(function(A) {
                    D.animate(A)
                });
                D.displayCanvasContext.clearRect(0, 0, D.displayCanvas.width, D.displayCanvas.height);
                D.displayCanvasContext.drawImage(D.renderCanvas, 0, -(D.renderCanvas.height / D.ratio - D.displayHeight) / 2);
                D.step()
            }, D.stepDelay)
        }, this.clear = function() {
            this.renderCanvasContext.fillStyle = "#fff";
            this.renderCanvasContext.clearRect(0, 0, this.renderCanvas.width, this.renderCanvas.height);
            this.displayCanvasContext.clearRect(0, 0, this.displayCanvas.width, this.displayCanvas.height)
        }, this.step = function(Q) {
            this.renderCanvasContext.fillStyle = "#fff";
            this.renderCanvasContext.clearRect(0, 0, this.renderCanvas.width, this.renderCanvas.height);
            var L = null;
            var O = 1;
            var V = 1;
            var N = 1;
            var P = 1;
            var M = 0;
            if (document.documentElement.className.indexOf("loading") < 0) {
                this.globalOpacity = this.globalOpacity > 0 ? this.globalOpacity - 10 : 0
            } else {
                this.globalOpacity = this.globalOpacity < 10 ? this.globalOpacity + 1 : 10
            }
            if (this.globalOpacity == 0) {
                this.stop();
                return
            }
            this.renderCanvasContext.globalAlpha = this.globalOpacity / 10;
            var S = typeof Q === "number" ? Q : 1;
            for (var U = 0; U < S; U++) {
                L = new Array();
                for (var T = 0; T < this.rows; T++) {
                    V = T == (this.rows - 1) ? -1 : T;
                    P = T == 0 ? this.rows : T;
                    for (var R = 0; R < this.cells; R++) {
                        O = R == (this.cells - 1) ? -1 : R;
                        N = R == 0 ? this.cells : R;
                        M = 0;
                        if (this.alive[T][N - 1] == 1) {
                            M += 1
                        }
                        if (this.alive[T][O + 1] == 1) {
                            M += 1
                        }
                        if (this.alive[V + 1][R] == 1) {
                            M += 1
                        }
                        if (this.alive[P - 1][R] == 1) {
                            M += 1
                        }
                        if (this.alive[P - 1][N - 1] == 1) {
                            M += 1
                        }
                        if (this.alive[V + 1][N - 1] == 1) {
                            M += 1
                        }
                        if (this.alive[V + 1][O + 1] == 1) {
                            M += 1
                        }
                        if (this.alive[P - 1][O + 1] == 1) {
                            M += 1
                        }
                        if (L[T] == undefined) {
                            L[T] = []
                        }
                        L[T][R] = 0;
                        if (this.alive[T][R] > 1) {
                            L[T][R] = (this.alive[T][R] + 1) % this.generations
                        } else {
                            if (!this.alive[T][R] && this.births.indexOf(M) != -1) {
                                L[T][R] = 1
                            } else {
                                if (this.alive[T][R] == 1) {
                                    if (this.survivors.indexOf(M) != -1) {
                                        L[T][R] = 1
                                    } else {
                                        L[T][R] = 2
                                    }
                                }
                            }
                        }
                        if (typeof Q === "undefined") {
                            if (L[T][R]) {
                                this.renderCanvasContext.drawImage(this.dots[L[T][R]], R * (this.size + 1), T * (this.size + 1))
                            }
                        }
                    }
                }
                this.alive = L;
                this.iterations++
            }
        }
    }
    var e, obj = document.createElement("div"),
        verIEfull = null;
    if (!verIEfull || parseInt(verIEfull) > 8) {
        var WolframAlphaLatencyAnimation = new LatencyAnimation();
        var startCycle = 0;
        WolframAlphaLatencyAnimation.init(document.getElementById("solutions"));
        WolframAlphaLatencyAnimation.start(false, startCycle, 0);
        var iterationsStorage = function(B) {
            localStorage.setItem("iterations", WolframAlphaLatencyAnimation.iterations.toString())
        };
        if (window.addEventListener) {
            window.addEventListener("unload", iterationsStorage)
        } else {
            if (window.attachEvent) {
                window.attachEvent("onunload", iterationsStorage)
            }
        }
    };
</script>