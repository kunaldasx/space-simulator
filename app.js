(function () {
	"use strict";

	/* STARS */
	var sf = document.createDocumentFragment();
	for (var i = 0; i < 200; i++) {
		var s = document.createElement("div");
		s.className = "st";
		var sz = (Math.random() * 2.2 + 0.4).toFixed(2);
		s.style.cssText =
			"width:" +
			sz +
			"px;height:" +
			sz +
			"px;top:" +
			(Math.random() * 100).toFixed(2) +
			"%;left:" +
			(Math.random() * 100).toFixed(2) +
			"%;--d:" +
			(Math.random() * 4 + 2).toFixed(1) +
			"s;--del:" +
			(Math.random() * 6).toFixed(1) +
			"s;opacity:" +
			(Math.random() * 0.5 + 0.1).toFixed(2);
		sf.appendChild(s);
	}
	document.getElementById("stars").appendChild(sf);

	/* SCENE SWITCH */
	var fade = document.getElementById("fade");
	var navigationTimer = null;
	var discovered = {};
	var sceneNames = {
		s1: "EARTH / LAUNCHPAD",
		s2: "LOW ORBIT / TRANSIT",
		s3: "SOLAR SYSTEM / INNER VIEW",
		s4: "DEEP FIELD / OBSERVABLE UNIVERSE",
	};
	var sceneKickers = {
		s1: "KNOWN SPACE",
		s2: "LOW ORBIT",
		s3: "SOLAR SYSTEM",
		s4: "THE OBSERVABLE UNIVERSE",
	};
	var sceneMeta = {
		s1: "A JOURNEY THROUGH THE OBSERVABLE UNIVERSE",
		s2: "EARTH DRIFT / READY FOR DEPARTURE",
		s3: "8 WORLDS MAPPED / TAP TO EXPLORE",
		s4: "93 BILLION LIGHT-YEARS / 2 TRILLION GALAXIES / 13.8 BILLION YEARS",
	};
	var sceneHints = {
		s3: "Tap any planet or the Sun to view details",
		s4: "Tap any object to view details",
	};
	function updateHud(id) {
		document.getElementById("hudScene").textContent =
			sceneNames[id] || "EXPLORER LOG";
		document.getElementById("hudKicker").textContent =
			sceneKickers[id] || "KNOWN SPACE";
		document.getElementById("hudMeta").textContent =
			sceneMeta[id] || "EXPLORATION CONSOLE";
		document.getElementById("interactionHint").style.display = sceneHints[id]
			? "flex"
			: "none";
		document.getElementById("interactionHintText").textContent =
			sceneHints[id] || "Tap any object to view details";
		document.body.classList.remove("focus-view");
		document.getElementById("viewToggle").style.display =
			id === "s3" || id === "s4" ? "inline-flex" : "none";
		var found = Object.keys(discovered).length;
		document.getElementById("hudCount").textContent = found + " / 18 found";
		document.getElementById("hudProgress").style.width =
			(found / 18) * 100 + "%";
	}
	function markDiscovered(id) {
		discovered[id] = true;
		updateHud(document.querySelector(".scene:not(.off)").id);
	}
	function go(id, delay) {
		delay = delay || 480;
		if (navigationTimer) clearTimeout(navigationTimer);
		fade.classList.add("on");
		updateHud(id);
		navigationTimer = setTimeout(function () {
			document.querySelectorAll(".scene").forEach(function (el) {
				el.classList.add("off");
			});
			document.getElementById(id).classList.remove("off");
			if (id === "s3") buildSolar();
			if (id === "s4") buildUniv();
			navigationTimer = setTimeout(function () {
				fade.classList.remove("on");
				navigationTimer = null;
			}, 60);
		}, delay);
	}

	/* DRAG TO LAUNCH */
	var rocket = document.getElementById("rocket");
	var rfEl = document.getElementById("rf");
	var cbar = document.getElementById("cbar");
	var cfill = document.getElementById("cfill");
	var clbl = document.getElementById("clbl");
	var smokeEl = document.getElementById("smoke");
	var THRESH = 82,
		MAXVIS = 55,
		active = false,
		launched = false,
		startY = 0,
		pull = 0;
	function setRY(px) {
		rocket.style.setProperty("--ry", px + "px");
	}
	function resetPull() {
		active = false;
		pull = 0;
		cbar.classList.remove("show");
		clbl.classList.remove("show");
		cfill.style.width = "0%";
		cfill.classList.remove("go");
		rfEl.style.borderTopWidth = "0px";
		rocket.style.transition = "transform .4s cubic-bezier(.34,1.5,.64,1)";
		setRY(0);
		setTimeout(function () {
			rocket.style.transition = "";
		}, 420);
	}
	function launch() {
		launched = true;
		active = false;
		cbar.classList.remove("show");
		clbl.classList.remove("show");
		rocket.style.transition = "";
		setRY(0);
		requestAnimationFrame(function () {
			requestAnimationFrame(function () {
				rocket.classList.add("up");
				smokeEl.classList.add("pop");
				setTimeout(function () {
					go("s2", 320);
				}, 2500);
			});
		});
	}
	rocket.addEventListener("pointerdown", function (e) {
		if (launched) return;
		active = true;
		startY = e.clientY;
		rocket.setPointerCapture(e.pointerId);
		rocket.style.transition = "";
		cbar.classList.add("show");
		clbl.classList.add("show");
		e.preventDefault();
	});
	rocket.addEventListener("pointermove", function (e) {
		if (!active || launched) return;
		e.preventDefault();
		var dy = e.clientY - startY;
		pull = dy < 0 ? 0 : dy;
		var vis = Math.min(pull * 0.62, MAXVIS);
		setRY(vis);
		var pct = Math.min((pull / THRESH) * 100, 100);
		cfill.style.width = pct + "%";
		if (pct >= 100) cfill.classList.add("go");
		else cfill.classList.remove("go");
		var fh = Math.round(pct * 0.36);
		rfEl.style.borderTopWidth = fh + "px";
		rfEl.style.borderTopStyle = "solid";
		rfEl.style.borderTopColor = pct < 55 ? "#ff6611" : "#ffcc00";
	});
	rocket.addEventListener("pointerup", function (e) {
		if (!active || launched) return;
		rocket.releasePointerCapture(e.pointerId);
		if (pull >= THRESH) launch();
		else resetPull();
	});
	rocket.addEventListener("pointercancel", function () {
		if (active) resetPull();
	});

	/* SCENE 2 */
	document.getElementById("btnSolar").addEventListener("click", function () {
		go("s3");
	});

	function lgt(h) {
		return (
			"#" +
			h.slice(1).replace(/../g, function (m) {
				return Math.min(255, parseInt(m, 16) + 48)
					.toString(16)
					.padStart(2, "0");
			})
		);
	}
	function drk(h) {
		return (
			"#" +
			h.slice(1).replace(/../g, function (m) {
				return Math.max(0, parseInt(m, 16) - 38)
					.toString(16)
					.padStart(2, "0");
			})
		);
	}

	function showModal(data) {
		markDiscovered(data.name);
		var mbg = document.getElementById("mbg");
		var mdisc = document.getElementById("mdisc");

		/* background gradient using planet/sun colour */
		var c1 = data.glow || data.color;
		var c2 = data.color2 || drk(data.color);
		mbg.style.background =
			"radial-gradient(ellipse at 50% 30%, " +
			c1 +
			"55 0%, " +
			c2 +
			"22 45%, #000 100%)";

		/* planet/sun disc */
		var discSz = Math.min(
			window.innerWidth * 0.42,
			window.innerHeight * 0.28,
			160,
		);
		discSz = Math.max(discSz, 80);
		mdisc.style.width = discSz + "px";
		mdisc.style.height = discSz + "px";
		if (data.isSun) {
			mdisc.style.background =
				"radial-gradient(circle at 38% 38%,#fffacc,#ffcc00,#ff8800,#ff3300)";
			mdisc.style.boxShadow =
				"0 0 " +
				discSz * 0.4 +
				"px #ffcc0099, 0 0 " +
				discSz * 0.8 +
				"px #ff880055";
		} else {
			mdisc.style.background =
				"radial-gradient(circle at 35% 35%," +
				lgt(data.color) +
				"," +
				data.color +
				"," +
				drk(data.color) +
				")";
			mdisc.style.boxShadow =
				"0 0 " + discSz * 0.35 + "px " + data.color + "88";
		}

		/* Saturn ring on disc */
		var existingRing = mdisc.querySelector(".m-disc-ring");
		if (existingRing) existingRing.remove();
		if (data.ring) {
			var dr = document.createElement("div");
			dr.className = "m-disc-ring";
			dr.style.cssText =
				"position:absolute;width:145%;height:28%;border-radius:50%;border:3px solid " +
				data.color +
				"66;top:36%;left:-22.5%;transform:rotateX(65deg);pointer-events:none";
			mdisc.style.position = "relative";
			mdisc.style.overflow = "visible";
			mdisc.appendChild(dr);
		} else {
			mdisc.style.overflow = "hidden";
		}

		document.getElementById("mtitle").textContent = data.name;
		document.getElementById("mtype").textContent = data.type;
		document.getElementById("mdesc").textContent = data.desc;

		var grid = document.getElementById("mgrid");
		grid.innerHTML = "";
		(data.stats || []).forEach(function (st) {
			var d = document.createElement("div");
			d.className = "mstat";
			d.innerHTML =
				'<div class="mslbl">' +
				st.l +
				'</div><div class="msval">' +
				st.v +
				"</div>";
			grid.appendChild(d);
		});

		var mf = document.getElementById("mfacts");
		mf.innerHTML = "";
		(data.facts || []).forEach(function (f) {
			var d = document.createElement("div");
			d.className = "mfact";
			d.textContent = f;
			mf.appendChild(d);
		});

		var mm = document.getElementById("mmystery");
		mm.innerHTML = "";
		if (data.mystery) {
			var sec = document.createElement("div");
			sec.className = "msec";
			sec.textContent = "Still a Mystery";
			mm.appendChild(sec);
			var mc = document.createElement("div");
			mc.className = "mmystery";
			mc.innerHTML =
				'<div class="mq">Question</div><div class="mqtxt">' +
				data.mystery.q +
				'</div><div class="mq" style="margin-top:10px">Why it matters</div><div class="mwhy">' +
				data.mystery.why +
				"</div>";
			mm.appendChild(mc);
		}

		document.getElementById("modal").classList.remove("off");
		document.getElementById("mbox").scrollTop = 0;
	}

	function closeModal() {
		document.getElementById("modal").classList.add("off");
		if (activePW) {
			activePW.style.animationPlayState = "running";
			activePW = null;
		}
	}
	document.getElementById("mclose").addEventListener("click", closeModal);
	document.getElementById("modal").addEventListener("click", function (e) {
		if (e.target === this) closeModal();
	});

	/* ════════════════════════════════
   SOLAR SYSTEM
════════════════════════════════ */
	var kfNodes = [],
		activePW = null;

	function buildSolar() {
		var el = document.getElementById("solar");
		el.innerHTML = "";
		kfNodes.forEach(function (n) {
			if (n.parentNode) n.parentNode.removeChild(n);
		});
		kfNodes = [];
		var vw = window.innerWidth,
			vh = window.innerHeight;
		var sz = Math.min(vw * 0.93, vh * 0.6, 520);
		el.style.width = sz + "px";
		el.style.height = sz + "px";
		var cx = sz / 2,
			sunSz = Math.max(18, sz * 0.076);

		var sun = document.createElement("div");
		sun.className = "sun-el";
		sun.style.cssText =
			"width:" +
			sunSz +
			"px;height:" +
			sunSz +
			"px;top:" +
			(cx - sunSz / 2) +
			"px;left:" +
			(cx - sunSz / 2) +
			"px";
		function openSun(e) {
			e.preventDefault();
			showModal(SUN);
		}
		sun.addEventListener("click", openSun);
		el.appendChild(sun);

		PLANETS.forEach(function (p, i) {
			var or = (sz * p.o) / 2,
				ps = Math.max(10, Math.round(sunSz * 0.43 * p.r));
			var ring = document.createElement("div");
			ring.className = "oring";
			ring.style.cssText =
				"width:" +
				or * 2 +
				"px;height:" +
				or * 2 +
				"px;top:" +
				(cx - or) +
				"px;left:" +
				(cx - or) +
				"px";
			el.appendChild(ring);
			var kn = "ob" + i + "_" + Date.now();
			var sd = (i / PLANETS.length) * 360;
			var kf = document.createElement("style");
			kf.textContent =
				"@keyframes " +
				kn +
				"{from{transform:rotate(" +
				sd +
				"deg) translateX(" +
				or +
				"px) rotate(-" +
				sd +
				"deg)}to{transform:rotate(" +
				(sd + 360) +
				"deg) translateX(" +
				or +
				"px) rotate(-" +
				(sd + 360) +
				"deg)}}";
			document.head.appendChild(kf);
			kfNodes.push(kf);
			var pw = document.createElement("div");
			pw.className = "pwrap";
			pw.style.cssText =
				"top:" +
				cx +
				"px;left:" +
				cx +
				"px;animation:" +
				kn +
				" " +
				p.p.toFixed(1) +
				"s linear infinite";
			var disc = document.createElement("div");
			disc.className = "planet";
			disc.style.cssText =
				"width:" +
				ps +
				"px;height:" +
				ps +
				"px;background:radial-gradient(circle at 35% 35%," +
				lgt(p.color) +
				"," +
				p.color +
				"," +
				drk(p.color) +
				");box-shadow:0 0 " +
				ps * 0.55 +
				"px " +
				p.color +
				"66;margin-left:" +
				-ps / 2 +
				"px;margin-top:" +
				-ps / 2 +
				"px";
			if (p.ring) {
				var sr = document.createElement("div");
				sr.className = "sring";
				disc.appendChild(sr);
			}
			var nm = document.createElement("div");
			nm.className = "pname";
			nm.textContent = p.name;
			disc.appendChild(nm);
			var hit = document.createElement("div");
			hit.className = "phit";
			disc.appendChild(hit);
			pw.appendChild(disc);
			el.appendChild(pw);
			(function (planet, wrap) {
				function open(e) {
					e.stopPropagation();
					e.preventDefault();
					if (activePW) activePW.style.animationPlayState = "running";
					activePW = wrap;
					wrap.style.animationPlayState = "paused";
					showModal(planet);
				}
				hit.addEventListener("click", open, false);
			})(p, pw);
		});
	}
	window.addEventListener("resize", function () {
		if (!document.getElementById("s3").classList.contains("off")) buildSolar();
	});

	document.getElementById("btnUniv").addEventListener("click", function () {
		go("s4", 650);
	});

	/* ════════════════════════════════
   UNIVERSE — Zoomable + Pannable
════════════════════════════════ */
	var uScale = 0.55,
		uMinScale = 0.25,
		uMaxScale = 5;
	var uPanX = 0,
		uPanY = 0;
	var uWorldEl = document.getElementById("uworld");
	var uCanvasEl = document.getElementById("ucanvas");

	function setUT() {
		uWorldEl.style.transform =
			"translate(calc(-50% + " +
			uPanX +
			"px), calc(-50% + " +
			uPanY +
			"px)) scale(" +
			uScale +
			")";
		document.getElementById("uzLabel").textContent = uScale.toFixed(2) + "x";
	}

	function buildUniv() {
		if (uWorldEl.dataset.built) return;
		uWorldEl.dataset.built = "1";

		/* Milky Way sphere */
		var mwSz = 200;
		var mw = document.createElement("div");
		mw.className = "umw";
		mw.style.cssText =
			"width:" +
			mwSz +
			"px;height:" +
			mwSz +
			"px;margin-left:" +
			-mwSz / 2 +
			"px;margin-top:" +
			-mwSz / 2 +
			"px;position:absolute";
		for (var i = 0; i < 55; i++) {
			var gc2 = document.createElement("div");
			gc2.className = "gc";
			var s = Math.random() * 22 + 3;
			gc2.style.cssText =
				"width:" +
				s +
				"px;height:" +
				s +
				"px;top:" +
				(Math.random() * 83 + 5).toFixed(1) +
				"%;left:" +
				(Math.random() * 83 + 5).toFixed(1) +
				"%;--d:" +
				(Math.random() * 6 + 4).toFixed(1) +
				"s;--gx:" +
				(Math.random() * 14 - 7).toFixed(0) +
				"px;--gy:" +
				(Math.random() * 14 - 7).toFixed(0) +
				"px;animation-delay:" +
				(Math.random() * 6).toFixed(1) +
				"s";
			mw.appendChild(gc2);
		}
		uWorldEl.appendChild(mw);

		/* all universe objects */
		UOBJECTS.forEach(function (obj) {
			var el = document.createElement("div");
			el.className = "uobj";
			var half = obj.sz / 2;
			var base =
				"left:" +
				obj.x +
				"px;top:" +
				obj.y +
				"px;width:" +
				obj.sz +
				"px;height:" +
				obj.sz +
				"px;margin-left:" +
				-half +
				"px;margin-top:" +
				-half +
				"px;";
			if (obj.type === "void") {
				el.style.cssText =
					base +
					"background:radial-gradient(circle,#080818,#000);border:1px dashed #ffffff18;border-radius:50%";
			} else if (obj.type === "background") {
				el.style.cssText =
					base +
					"background:radial-gradient(circle," +
					obj.color +
					"88,transparent);border-radius:50%;opacity:.6;border:1px solid " +
					obj.color +
					"33";
			} else if (obj.type === "filament") {
				el.style.cssText =
					base +
					"background:linear-gradient(135deg," +
					obj.color +
					"55," +
					obj.glow +
					"22,transparent);border-radius:35%;border:1px solid " +
					obj.color +
					"44";
			} else {
				el.style.cssText =
					base +
					"background:radial-gradient(circle at 38% 38%," +
					obj.glow +
					"cc," +
					obj.color +
					"88," +
					obj.color +
					"22);box-shadow:0 0 " +
					obj.sz * 0.3 +
					"px " +
					obj.glow;
			}
			/* Keep smaller targets above broad-scale structures for reliable selection. */
			el.style.zIndex = String(1000 - obj.sz);
			if (obj.id === "milkyway") {
				var homeMarker = document.createElement("div");
				homeMarker.className = "home-marker";
				var dot = document.createElement("div");
				dot.className = "udot";
				dot.addEventListener("click", function (event) {
					event.stopPropagation();
					showModal(PLANETS[2]);
				});
				var hereWrap = document.createElement("div");
				hereWrap.className = "uhere-wrap";
				var h1 = document.createElement("div");
				h1.className = "uhere";
				h1.textContent = "you are here";
				var h2 = document.createElement("div");
				h2.className = "uhere-fact";
				h2.textContent = "Solar System";
				hereWrap.appendChild(h1);
				hereWrap.appendChild(h2);
				homeMarker.appendChild(dot);
				homeMarker.appendChild(hereWrap);
				el.appendChild(homeMarker);
			}

			/* label + key fact */
			var info = document.createElement("div");
			info.className = "uobj-info";
			var nameLine = document.createElement("div");
			nameLine.className = "uobj-name";
			nameLine.textContent = obj.label;
			var factLine = document.createElement("div");
			factLine.className = "uobj-keyfact";
			factLine.textContent = obj.keyfact;
			info.appendChild(nameLine);
			info.appendChild(factLine);
			el.appendChild(info);
			uWorldEl.appendChild(el);

			(function (o) {
				function openU(e) {
					e.stopPropagation();
					e.preventDefault();
					showUFloat(o);
				}
				el.addEventListener("click", openU, false);
			})(obj);
		});

		uScale = 0.55;
		uPanX = 0;
		uPanY = 0;
		setUT();
	}

	/* ── UNIVERSE FLOAT PANEL ── */
	function showUFloat(obj) {
		markDiscovered(obj.id);
		var d = obj.data;
		var disc = document.getElementById("uf-disc");
		var discSz = 52;
		disc.style.width = discSz + "px";
		disc.style.height = discSz + "px";
		if (obj.type === "void") {
			disc.style.background = "radial-gradient(circle,#0a0a1a,#000)";
			disc.style.border = "1px dashed #ffffff22";
			disc.style.boxShadow = "none";
		} else if (obj.type === "background") {
			disc.style.background =
				"radial-gradient(circle," + obj.color + "99,transparent)";
			disc.style.border = "1px solid " + obj.color + "44";
			disc.style.boxShadow = "none";
		} else if (obj.type === "filament") {
			disc.style.background =
				"linear-gradient(135deg," + obj.color + "88," + obj.glow + "44)";
			disc.style.border = "1px solid " + obj.color + "55";
			disc.style.boxShadow = "none";
			disc.style.borderRadius = "40%";
		} else {
			disc.style.background =
				"radial-gradient(circle at 35% 35%," +
				obj.glow +
				"dd," +
				obj.color +
				"99," +
				obj.color +
				"22)";
			disc.style.border = "none";
			disc.style.borderRadius = "50%";
			disc.style.boxShadow = "0 0 16px " + obj.glow + "99";
		}
		document.getElementById("uf-name").textContent = d.name;
		document.getElementById("uf-name").style.color = obj.color || "#fff";
		document.getElementById("uf-type").textContent = d.type;
		document.getElementById("uf-keyfact").textContent = obj.keyfact;
		document.getElementById("uf-desc").textContent = d.desc;
		var grid = document.getElementById("uf-grid");
		grid.innerHTML = "";
		(d.stats || []).forEach(function (st) {
			var el2 = document.createElement("div");
			el2.className = "uf-stat";
			el2.innerHTML =
				'<div class="uf-slbl">' +
				st.l +
				'</div><div class="uf-sval">' +
				st.v +
				"</div>";
			grid.appendChild(el2);
		});
		var ff = document.getElementById("uf-facts");
		ff.innerHTML = "";
		(d.facts || []).forEach(function (f) {
			var el2 = document.createElement("div");
			el2.className = "uf-fact";
			el2.textContent = f;
			ff.appendChild(el2);
		});
		var fm = document.getElementById("uf-mystery");
		fm.innerHTML = "";
		if (d.mystery) {
			var sec = document.createElement("div");
			sec.className = "uf-sec";
			sec.textContent = "Still a Mystery";
			fm.appendChild(sec);
			var mc = document.createElement("div");
			mc.className = "uf-mystery";
			mc.innerHTML =
				'<div class="uf-mq">Question</div><div class="uf-mqtxt">' +
				d.mystery.q +
				'</div><div class="uf-mq" style="margin-top:8px">Why it matters</div><div class="uf-mwhy">' +
				d.mystery.why +
				"</div>";
			fm.appendChild(mc);
		}
		var panel = document.getElementById("ufloat");
		panel.scrollTop = 0;
		panel.classList.add("open");
	}
	document.getElementById("ufClose").addEventListener("click", function () {
		document.getElementById("ufloat").classList.remove("open");
	});

	document
		.querySelectorAll(".u-controls,#btnBack,#ufloat")
		.forEach(function (el) {
			el.addEventListener("pointerdown", function (e) {
				e.stopPropagation();
			});
		});

	/* zoom buttons */
	document.getElementById("uzIn").addEventListener("click", function () {
		uScale = Math.min(uMaxScale, uScale * 1.5);
		setUT();
	});
	document.getElementById("uzOut").addEventListener("click", function () {
		uScale = Math.max(uMinScale, uScale / 1.5);
		setUT();
	});
	document.getElementById("uzReset").addEventListener("click", function () {
		uScale = 0.55;
		uPanX = 0;
		uPanY = 0;
		setUT();
	});

	/* back to earth — full rocket reset then go to launch screen */
	document.getElementById("btnBack").addEventListener("click", function () {
		document.getElementById("ufloat").classList.remove("open");
		// 1. reset all drag state
		launched = false;
		active = false;
		pull = 0;
		// 2. strip the liftoff animation cleanly
		rocket.style.animation = "none";
		rocket.classList.remove("up");
		// 3. clear inline styles set during drag/launch
		rocket.style.transition = "none";
		setRY(0);
		rfEl.style.borderTopStyle = "solid";
		rfEl.style.borderTopWidth = "0px";
		rfEl.style.borderTopColor = "transparent";
		// 4. reset charge bar + smoke
		cfill.style.width = "0%";
		cfill.classList.remove("go");
		cbar.classList.remove("show");
		clbl.classList.remove("show");
		smokeEl.classList.remove("pop");
		smokeEl.style.animation = "none";
		// 5. force browser to flush the style reset before re-enabling transitions
		void rocket.offsetWidth;
		rocket.style.animation = "";
		rocket.style.transition = "";
		smokeEl.style.animation = "";
		uScale = 0.55;
		uPanX = 0;
		uPanY = 0;
		setUT();
		go("s1", 500);
	});

	/* pan + pinch */
	var uPanning = false,
		uPinching = false,
		uLastX = 0,
		uLastY = 0,
		uLastDist = 0;
	function getPinchDist(e) {
		var dx = e.touches[0].clientX - e.touches[1].clientX;
		var dy = e.touches[0].clientY - e.touches[1].clientY;
		return Math.sqrt(dx * dx + dy * dy);
	}
	/* mouse/pointer pan */
	uCanvasEl.addEventListener("pointerdown", function (e) {
		if (e.pointerType === "touch") return;
		if (e.target.closest("button,.uobj,.udot,#ufloat")) return;
		document.getElementById("ufloat").classList.remove("open");
		uPanning = true;
		uLastX = e.clientX;
		uLastY = e.clientY;
		uCanvasEl.setPointerCapture(e.pointerId);
	});
	uCanvasEl.addEventListener("pointermove", function (e) {
		if (!uPanning) return;
		uPanX += e.clientX - uLastX;
		uPanY += e.clientY - uLastY;
		uLastX = e.clientX;
		uLastY = e.clientY;
		setUT();
	});
	uCanvasEl.addEventListener("pointerup", function () {
		uPanning = false;
	});
	uCanvasEl.addEventListener("pointercancel", function () {
		uPanning = false;
	});
	/* touch pan + pinch */
	uCanvasEl.addEventListener(
		"touchstart",
		function (e) {
			if (e.touches.length === 2) {
				uPinching = true;
				uPanning = false;
				uLastDist = getPinchDist(e);
			} else if (e.touches.length === 1) {
				uPanning = true;
				uLastX = e.touches[0].clientX;
				uLastY = e.touches[0].clientY;
			}
		},
		{ passive: true },
	);
	uCanvasEl.addEventListener(
		"touchmove",
		function (e) {
			if (uPinching && e.touches.length === 2) {
				e.preventDefault();
				var d = getPinchDist(e);
				uScale = Math.min(
					uMaxScale,
					Math.max(uMinScale, uScale * (d / uLastDist)),
				);
				uLastDist = d;
				setUT();
			} else if (uPanning && e.touches.length === 1) {
				uPanX += e.touches[0].clientX - uLastX;
				uPanY += e.touches[0].clientY - uLastY;
				uLastX = e.touches[0].clientX;
				uLastY = e.touches[0].clientY;
				setUT();
			}
		},
		{ passive: false },
	);
	uCanvasEl.addEventListener(
		"touchend",
		function (e) {
			if (e.touches.length < 2) uPinching = false;
			if (e.touches.length === 0) uPanning = false;
		},
		{ passive: true },
	);
	/* scroll wheel */
	uCanvasEl.addEventListener(
		"wheel",
		function (e) {
			if (e.target.closest("#ufloat")) return;
			e.preventDefault();
			uScale = Math.min(
				uMaxScale,
				Math.max(uMinScale, uScale * (e.deltaY > 0 ? 0.85 : 1.18)),
			);
			setUT();
		},
		{ passive: false },
	);

	/* OBJECT CATALOG + DISCOVERY */
	var searchPanel = document.getElementById("searchPanel");
	var searchInput = document.getElementById("objectSearch");
	var searchResults = document.getElementById("searchResults");
	var catalog = [{ name: SUN.name, type: SUN.type, data: SUN, scene: "s3" }];
	PLANETS.forEach(function (planet) {
		catalog.push({
			name: planet.name,
			type: planet.type,
			data: planet,
			scene: "s3",
		});
	});
	UOBJECTS.forEach(function (object) {
		catalog.push({
			name: object.label,
			type: object.type,
			data: object,
			scene: "s4",
		});
	});
	function openDiscovery(item) {
		searchPanel.classList.remove("open");
		searchPanel.setAttribute("aria-hidden", "true");
		if (item.scene === "s3") {
			go("s3", 220);
			setTimeout(function () {
				showModal(item.data);
			}, 320);
		} else {
			go("s4", 220);
			setTimeout(function () {
				focusUniverse(item.data);
			}, 320);
		}
	}
	function renderSearch(query) {
		var term = query.trim().toLowerCase();
		var matches = catalog
			.filter(function (item) {
				return (
					!term ||
					(item.name + " " + item.type).toLowerCase().indexOf(term) !== -1
				);
			})
			.slice(0, 8);
		searchResults.innerHTML = "";
		if (!matches.length) {
			var empty = document.createElement("div");
			empty.className = "search-empty";
			empty.textContent = "No objects match that signal.";
			searchResults.appendChild(empty);
			return;
		}
		matches.forEach(function (item) {
			var result = document.createElement("button");
			result.className = "search-result";
			result.type = "button";
			result.innerHTML =
				"<span>" +
				item.name +
				"</span><small>" +
				item.scene.replace("s", "") +
				" / " +
				item.type +
				"</small>";
			result.addEventListener("click", function () {
				openDiscovery(item);
			});
			searchResults.appendChild(result);
		});
	}
	document
		.getElementById("hudSearchToggle")
		.addEventListener("click", function () {
			var open = searchPanel.classList.toggle("open");
			searchPanel.setAttribute("aria-hidden", String(!open));
			if (open) {
				searchInput.focus();
				renderSearch(searchInput.value);
			}
		});
	document.getElementById("viewToggle").addEventListener("click", function () {
		var focused = document.body.classList.toggle("focus-view");
		if (focused) {
			searchPanel.classList.remove("open");
			searchPanel.setAttribute("aria-hidden", "true");
		}
		this.textContent = focused ? "EXIT FOCUS" : "FOCUS";
		this.setAttribute(
			"aria-label",
			focused ? "Exit full view" : "Enter full view",
		);
	});
	document.getElementById("searchClose").addEventListener("click", function () {
		searchPanel.classList.remove("open");
		searchPanel.setAttribute("aria-hidden", "true");
	});
	searchInput.addEventListener("input", function () {
		renderSearch(searchInput.value);
	});
	document.getElementById("discoverBtn").addEventListener("click", function () {
		openDiscovery(catalog[Math.floor(Math.random() * catalog.length)]);
	});
	document.getElementById("solarEarth").addEventListener("click", function () {
		showModal(PLANETS[2]);
	});
	document.getElementById("solarRandom").addEventListener("click", function () {
		showModal(PLANETS[Math.floor(Math.random() * PLANETS.length)]);
	});
	document
		.getElementById("universeRandom")
		.addEventListener("click", function () {
			openDiscovery(
				catalog[
					PLANETS.length + 1 + Math.floor(Math.random() * UOBJECTS.length)
				],
			);
		});
	document.addEventListener("keydown", function (event) {
		if (event.key !== "Escape") return;
		var viewToggle = document.getElementById("viewToggle");
		if (document.body.classList.contains("focus-view")) {
			document.body.classList.remove("focus-view");
			viewToggle.textContent = "FOCUS";
			viewToggle.setAttribute("aria-label", "Enter full view");
		}
		searchPanel.classList.remove("open");
		searchPanel.setAttribute("aria-hidden", "true");
		closeModal();
		document.getElementById("ufloat").classList.remove("open");
	});
	function focusUniverse(object) {
		var target = object || UOBJECTS[0];
		uPanX = -target.x * uScale;
		uPanY = -target.y * uScale;
		setUT();
		showUFloat(target);
	}
	updateHud("s1");
})();
