from . import (star, single, persona_star, proposer_critic, tournament, tree,
               chain, cascading_chain, diamond)

ARCHITECTURES = {
    "star": star.run,
    "single": single.run,
    "persona_star": persona_star.run,
    "proposer_critic": proposer_critic.run,
    "tournament": tournament.run,
    "tree": tree.run,
    "chain": chain.run,
    "cascading_chain": cascading_chain.run,
    "diamond": diamond.run,
}
