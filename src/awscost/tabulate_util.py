from tabulate import tabulate


class TabulateUtil:
    @staticmethod
    def convert(results, tablefmt="simple"):
        converts = []
        for k, amounts in results.items():
            converts.append(dict({"key": k}, **amounts))
        last_time = list(converts[0].keys())[-1]
        converts = sorted(
            converts,
            key=lambda x: 0 if x.get(last_time) is None else x.get(last_time),
            reverse=True,
        )
        return tabulate(converts, headers="keys", tablefmt=tablefmt)
