import matplotlib.pyplot as plt


class DrawGraph:
    def_style = ["-", "--", "-.", ":"]
    mm2inch = 0.03937007874  # 1/25.4

    def __init__(self):
        pass

    def draw(self, p_path, g_path, st, gr, x, df):
        plt.figure(figsize=(st["graph_size"][0]*self.mm2inch,
                            st["graph_size"][1]*self.mm2inch))
        plt.rcParams["font.family"] = st["font_family"]
        plt.rcParams["font.size"] = st["font_size"]

        if "subplot" in gr:
            self.multi_draw(p_path, st, gr["subplot"], x, df)
        else:
            self.single_draw(p_path, st, gr, x, df)

        plt.savefig(g_path)
        plt.close()

    def multi_draw(self, p_path, st, gr, x, df):
        for g in gr:
            plt.subplot(g["grid"][0], g["grid"][1], g["grid"][2])
            self.single_draw(p_path, st, g, x, df)

    def single_draw(self, p_path, st, gr, x, df):
        if gr["type"] == "plot":
            self.plot(p_path, st, gr, x, df)
        else:
            print("error: type'", gr["type"], "'does not correspond")

    # plot line graph
    def plot(self, p_path, st, gr, x, df):
        def_num = 0
        plt.xlabel(gr["xlabel"])
        plt.ylabel(gr["ylabel"])
        for grp in gr["elem"]:
            if grp["style"] == "order":
                grp["style"] = self.def_style[def_num]
                def_num = def_num + 1 if def_num < 3 else 0

            if type(grp["color"]) is int:
                color = "C"+str(grp["color"])
            else:
                color = grp["color"]

            if type(grp["col"]) is str:
                if not grp["col"] in df.columns:
                    print("error: column'", grp["col"], "' is not exist in", p_path)
                    continue
            elif type(grp["col"]) is int:
                if grp["col"] > len(df.columns):
                    print("error: out of bounds column'", grp["col"], "in", p_path)
                    continue
            else:
                print("error: Specify plot column by string or integer",
                      grp["col"], "in", p_path)
                continue

            plt.plot(
                x, df.ix[:, grp["col"]],
                label=grp["label"], color=color,
                linestyle=grp["style"], linewidth=grp["width"]
            )
        plt.xlim(st["xlim"])
        plt.ylim(gr["ylim"])

        if gr["legend"]["loc"] is not None:
            plt.legend(loc=gr["legend"]["loc"],
                       bbox_to_anchor=gr["legend"]["bbox_to_anchor"],
                       ncol=gr["legend"]["ncol"])

    # PLAN: scatter, bar, 3D(surface, wire frame, bar)
