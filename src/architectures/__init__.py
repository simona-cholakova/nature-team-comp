from . import star, single, persona_star

ARCHITECTURES = {
    "star": star.run,
    "single": single.run,
    "persona_star": persona_star.run,
}