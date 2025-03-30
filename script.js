import Lenis from "lenis";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

document.addEventListener("DOMContentLoaded", () => {
    if (window.innerWidth > 768) {
        const lenis = new Lenis();
        const videoContainer = document.querySelector(".video-container-desktop");
        const videoTitleElement = document.querySelector(".video-title p");

        lenis.on("scroll", ScrollTrigger.update);

        gsap.ticker.add((time) => {
            lenis.raf(time * 1000);
        });

        gsap.ticker.lagSmoothing(0);

        const breakpoints = [
            { maxwidth: 1000, translateY: -135, movMultiplier: 450 },
            { maxwidth: 1100, translateY: -130, movMultiplier: 500 },
            { maxwidth: 1200, translateY: -125, movMultiplier: 550 },
            { maxwidth: 1300, translateY: -120, movMultiplier: 600 },
        ];

        const getInitialValue = () => {
            const width = window.innerWidth;
            for (const bp of breakpoints) {
                if (width <= bp.maxwidth) {
                    return {
                        translateY: bp.translateY,
                        movMultiplier: bp.movMultiplier,
                    };
                }
            }
            return {
                translateY: -110,
                movMultiplier: 650,
            };
        };

        const initialValues = getInitialValue();

        const animationState = {
            scrollprogress: 0,
            initialtranslateY: initialValues.translateY,
            currentTranslateY: initialValues.translateY,
            movementMultiplier: initialValues.movMultiplier,
            scale: 0.25,
            fontSize: 80,
            gap: 2,
            targetMouseX: 0,
            currentMouseX: 0,
        };

        window.addEventListener("resize", () => {
            const newValues = getInitialValue();
            animationState.initialtranslateY = newValues.translateY;
            animationState.movementMultiplier = newValues.movMultiplier;

            if (animationState.scrollprogress === 0) {
                animationState.currentTranslateY = newValues.translateY;
            }
        });

        gsap.timeline({
            scrollTrigger: {
                trigger: "intro",
                start: "top bottom",
                end: "top 10%",
                scrub: true,
                onUpdate: (self) => {
                    animationState.scrollprogress = self.progress;
                    animationState.currentTranslateY = gsap.utils.interpolate(
                        animationState.initialtranslateY,
                        0,
                        animationState.scrollprogress
                    );

                    animationState.scale = gsap.utils.interpolate(
                        0.25,
                        1,
                        animationState.scrollprogress
                    );
                    animationState.fontSize = gsap.utils.interpolate(
                        2,
                        1,
                        animationState.scrollprogress
                    );

                    if (animationState.scrollprogress <= 0.4) {
                        const firstPartProgress = animationState.scrollprogress / 0.4;
                        animationState.fontSize = gsap.utils.interpolate(
                            80,
                            40,
                            firstPartProgress
                        );
                    } else {
                        const secondPartProgress = (animationState.scrollprogress - 0.4) / 0.6;
                        animationState.fontSize = gsap.utils.interpolate(
                            40,
                            80,
                            secondPartProgress
                        );
                    }
                },
            },
        });

        document.addEventListener("mousemove", (e) => {
            animationState.targetMouseX = ((e.clientX / window.innerWidth) - 0.5) * 2;
        });

        const animate = () => {
            if (window.innerWidth < 900) return;

            const {
                scale,
                targetMouseX,
                currentMouseX,
                currentTranslateY,
                fontSize,
                gap,
                movementMultiplier,
            } = animationState;

            const scaleMovementMultiplier = (1 - scale) * movementMultiplier;
            const maxHorizontalMovement = scale < 0.95 ? targetMouseX * scaleMovementMultiplier : 0;

            animationState.currentMouseX = gsap.utils.interpolate(
                animationState.currentMouseX,
                maxHorizontalMovement,
                0.05
            );

            videoContainer.style.transform = `translateY(${currentTranslateY}px) translateX(${animationState.currentMouseX}px) scale(${scale})`;
            videoContainer.style.gap = `${gap}em`;
            videoTitleElement.style.fontSize = `${fontSize}px`;

            requestAnimationFrame(animate);
        };
        animate();
    }
});
