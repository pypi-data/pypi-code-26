import itertools
import collections
import random
import functools
import itertools
class Agent:

        def __init__(self, hypothesis, active):

                self.hypothesis = hypothesis

                self.active = active

        def initialise(agent_count):

                return [
                        Agent(hypothesis=None, active=False)
                        for _
                        in range(agent_count)
                ]
def test_phase(
        swarm,
        microtests,
        random,
        multitesting=1,
        multitest_function=None
):

        if multitesting == 1:

                for agent in swarm:

                        microtest = random.choice(microtests)

                        agent.active = microtest(agent.hypothesis)

        else:

                for agent in swarm:

                        agent.active = multitest_function(
                                random.choice(microtests)(agent.hypothesis)
                                for test_num
                                in range(multitesting)
                        )
def scalar_test_phase(swarm, microtests, random):

        scores = [
                random.choice(microtests)(agent.hypothesis)
                for agent
                in swarm
        ]

        for agent, score in zip(swarm, scores):

                agent.active = score > random.choice(scores)
def passive_diffusion(swarm, random, random_hypothesis_function):

        for agent in swarm:

                if not agent.active:

                        random_agent = random.choice(swarm)

                        if random_agent.active:

                                agent.hypothesis = random_agent.hypothesis

                        else:

                                agent.hypothesis = random_hypothesis_function(random)
def context_free_diffusion(swarm, random, random_hypothesis_function):

        old_swarm = [(agent.hypothesis, agent.active) for agent in swarm]

        for agent in swarm:

                polled_hypothesis, polled_active = random.choice(old_swarm)

                if agent.active:

                        if polled_active:

                                agent.active = False

                                agent.hypothesis = random_hypothesis_function(random)

                else:

                        if polled_active:

                                agent.hypothesis = polled_hypothesis

                        else:

                                agent.hypothesis = random_hypothesis_function(random)
def context_sensitive_diffusion(
        swarm,
        random,
        random_hypothesis_function
):

        old_swarm = [(agent.hypothesis, agent.active) for agent in swarm]

        for agent in swarm:

                polled_hypothesis, polled_active = random.choice(old_swarm)

                if agent.active:

                        if (
                                polled_active
                                and polled_hypothesis == agent.hypothesis):

                                agent.active = False

                                new_hypothesis = random_hypothesis_function(random)

                else:

                        if polled_active:

                                agent.hypothesis = polled_hypothesis

                        else:

                                agent.hypothesis = random_hypothesis_function(random)
def multi_diffusion(
        swarm,
        random,
        random_hypothesis_function,
        multiplier,
):

        for agent in swarm:

                if not agent.active:

                        diffusion_count = 0

                        for diffusion_count in range(int(multiplier)):

                                random_agent = random.choice(swarm)

                                if random_agent.active:

                                        agent.hypothesis = random_agent.hypothesis
                                        break

                        else: # if for loop has not called break

                                random_agent = random.choice(swarm)

                                if (
                                        random_agent.active
                                        and random.random() < (multiplier-diffusion_count)
                                ):

                                        agent.hypothesis = random_agent.hypothesis

                                else:

                                        agent.hypothesis = random_hypothesis_function(random)
def iterate(
        swarm,
        microtests,
        random_hypothesis_function,
        diffusion_function,
        random,
        test_phase_function=test_phase,
):
        diffusion_function(swarm, random, random_hypothesis_function)

        test_phase_function(swarm, microtests, random)
def run(
        swarm,
        microtests,
        random_hypothesis_function,
        max_iterations,
        diffusion_function,
        random,
        multitesting=1,
        multitest_function=all,
        report_iterations=None,
        test_phase_function=test_phase,
        hypothesis_string_function=str,
        max_cluster_report=None,
):

        if max_iterations is None:

                iterator = itertools.count()

        else:

                iterator = range(max_iterations)

        try:

                for iteration in iterator:

                        diffusion_function(
                                swarm=swarm,
                                random=random,
                                random_hypothesis_function=random_hypothesis_function,
                        )

                        test_phase_function(
                                swarm=swarm,
                                microtests=microtests,
                                random=random,
                                multitesting=multitesting,
                                multitest_function=multitest_function,
                        )

                        if report_iterations:

                                if iteration % report_iterations == 0:

                                        clusters = count_clusters(swarm)

                                        agent_count = len(swarm)

                                        print("{i:4} Activity: {a:0.3f}. {c}".format(
                                                i=iteration,
                                                a=sum(clusters.values())/agent_count,
                                                c=", ".join(
                                                        "{hyp}:{count}".format(
                                                                hyp=hypothesis_string_function(hyp),
                                                                count=count
                                                        )
                                                        for hyp,count
                                                        in clusters.most_common(max_cluster_report)
                                                ),
                                        ))

        except KeyboardInterrupt:

                pass

        return count_clusters(swarm)
def count_clusters(swarm):

        return collections.Counter(
                agent.hypothesis
                for agent
                in swarm
                if agent.active
        )
def pretty_print_with_values(clusters, search_space, max_clusters=None):

        string_template = "{c:6d} at hyp {h:6d} (value: {e:0.6f})"

        cluster_strings = [
                string_template.format(
                        c=count,
                        h=hyp,
                        e=search_space[hyp])
                for hyp, count
                in clusters.most_common(max_clusters)
        ]

        return "\n".join(cluster_strings)
def simulate(
        scores,
        max_iterations=1000,
        report_iterations=500,
        diffusion_function=passive_diffusion,
        agent_count=1000,
        multitesting=1,
        multitest_function=all,
        random=random,
        random_hyp=None
):

        if random_hyp is None:

                random_hyp = lambda rnd: rnd.randrange(1,len(scores))

        def make_microtest(test_num, rnd):
                return lambda hyp: rnd.random() < scores[test_num]

        microtests = [
                lambda hyp: random.random() < scores[hyp]
        ]

        swarm=Agent.initialise(agent_count=agent_count)

        swarm[0].active = True
        swarm[0].hypothesis = 0

        clusters = run(
                swarm=swarm,
                microtests=microtests,
                random_hypothesis_function=random_hyp,
                max_iterations=max_iterations,
                diffusion_function=passive_diffusion,
                multitesting=multitesting,
                multitest_function=multitest_function,
                random=random,
                report_iterations=report_iterations,
        )

        return clusters
class Swarm:
        def __init__(self, size, random_hypothesis_function, lower_layer=None):

                self.agents = [
                        Agent(active=False, hypothesis=None)
                        for _
                        in range(size)
                ]

                if lower_layer is None:

                        lower_layer = []

                self.lower_layer = lower_layer

                self.random_hypothesis = random_hypothesis_function

        @staticmethod
        def passive_diffusion(swarm, solitarity, random):

                for agent_num, agent in enumerate(swarm.agents):

                        if not agent.active:

                                polled_agent = random.choice(swarm.agents)

                                if polled_agent.active and random.random() > solitarity:

                                        swarm.set_hypothesis(agent_num, polled_agent.hypothesis)

                                else:

                                        agent.hypothesis = swarm.random_hypothesis(
                                                agent_num,
                                                random,
                                        )

        @staticmethod
        def context_free_diffusion(swarm, random):

                for agent_num, agent in enumerate(swarm.agents):

                        polled_agent = random.choice(swarm.agents)

                        if agent.active:

                                if polled_agent.active:

                                        swarm.set_activity(agent_num, False)

                                        agent.hypothesis = swarm.random_hypothesis(
                                                agent_num,
                                                random,
                                        )

                        else:

                                if polled_agent.active:

                                        swarm.set_hypothesis(agent_num, polled_agent.hypothesis)

                                else:

                                        agent.hypothesis = swarm.random_hypothesis(
                                                agent_num,
                                                random,
                                        )

        @staticmethod
        def context_sensitive_diffusion(swarm, random):

                for agent_num, agent in enumerate(swarm.agents):

                        polled_agent = random.choice(swarm.agents)

                        if agent.active:

                                if (
                                        polled_agent.active
                                        and (agent.hypothesis == polled_agent.hypothesis)
                                ):


                                        swarm.set_activity(agent_num, False)

                                        agent.hypothesis = swarm.random_hypothesis(
                                                agent_num,
                                                random,
                                        )

                        else:

                                if polled_agent.active:

                                        swarm.set_hypothesis(agent_num, polled_agent.hypothesis)

                                else:

                                        agent.hypothesis = swarm.random_hypothesis(
                                                agent_num,
                                                random,
                                        )

        def test(self, microtests, random, multitest=1, multitest_fun=None):

                for num, agent in enumerate(self.agents):

                        microtest = random.choice(microtests)

                        if multitest == 1:

                                self.set_activity(num, microtest(agent.hypothesis))

                        else:

                                self.set_activity(
                                        num,
                                        multitest_fun(
                                                random.choice(microtests)(agent.hypothesis)
                                                for _
                                                in range(multitest)
                                        )
                                )



        def iterate(
                self,
                microtests,
                random,
                diffusion_function=passive_diffusion.__func__,
                multitest=1,
                multitest_fun=None,
                solitarity=1,
        ):
                diffusion_function(self, solitarity, random)
                self.test(microtests, random, multitest, multitest_fun)

        def set_activity(self, agent_num, new_activity):

                self.agents[agent_num].active = new_activity

                for swarm in self.lower_layer:

                        swarm.set_activity(agent_num, new_activity)

        def set_hypothesis(self, agent_num, new_hypothesis):

                self.agents[agent_num].hypothesis = new_hypothesis

                if len(self.lower_layer) == 0:
                        return

                for lower_swarm, hypothesis_component in (
                        zip(self.lower_layer,new_hypothesis)):

                        lower_swarm.set_hypothesis(agent_num, hypothesis_component)
def make_ml_sds(swarm_size, bottom_hyp_functions, topology):

        lower_layer = [
                Swarm(
                        size=swarm_size,
                        random_hypothesis_function=hyp_fun
                )
                for hyp_fun
                in bottom_hyp_functions
        ]

        for layer_num, swarm_splits in enumerate(topology,start=1):

                layer = []

                swarm_offset = 0

                for split_num, swarm_split in enumerate(swarm_splits):

                        lower_layer_start = swarm_offset

                        lower_layer_end = swarm_offset+swarm_split

                        random_hypothesis_function = functools.partial(
                                random_compound_hyp,
                                lower_layer[lower_layer_start:lower_layer_end],
                        )

                        new_swarm = Swarm(
                                size=swarm_size,
                                lower_layer=lower_layer[lower_layer_start:lower_layer_end],
                                random_hypothesis_function=random_hypothesis_function)

                        layer.append(new_swarm)

                        swarm_offset += swarm_split

                lower_layer = layer

        top_swarm = lower_layer[0]

        return top_swarm
def single_diffusion(agent_num, swarm, random):

        # agent is guaranteed to be inactive
        agent = swarm.agents[agent_num]

        polled_agent = random.choice(swarm.agents)

        if polled_agent.active:

                swarm.set_hypothesis(agent_num,polled_agent.hypothesis)

                return polled_agent.hypothesis

        else:

                new_hyp = swarm.random_hypothesis(agent_num, random)

                agent.hypothesis = new_hyp

                return new_hyp
def random_compound_hyp(lower_swarms, num, random):

        return tuple(
                single_diffusion(num, lower_swarm, random)
                for lower_swarm
                in lower_swarms
        )
def flatten_hypothesis(hypothesis,times):
        new_hypothesis = itertools.chain.from_iterable(hypothesis)
        if times == 1:
                return list(new_hypothesis)
        else:
                return flatten_hypothesis(new_hypothesis,times-1)
